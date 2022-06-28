import functools
import sys
import threading
import warnings
from collections import Counter, OrderedDict, defaultdict
from functools import partial

from django.core.exceptions import AppRegistryNotReady, ImproperlyConfigured

from .config import AppConfig


class Apps:
    """
    存储已安装应用程序配置的注册表。

     它还跟踪模型，例如 提供反向关系。 e.g. to provide reverse relations.
    """

    def __init__(self, installed_apps=()):
        # 在创建主注册表时，installed_apps设置为None，因为此时无法填充它。 其他注册表必须提供已安装应用程序的列表，并立即填充。
        if installed_apps is None and hasattr(sys.modules[__name__], 'apps'):
            raise RuntimeError("You must supply an installed_apps argument.")

        ''' 
        应用标签的映射=>模型名称=>模型类。 每次导入模型时，ModelBase .__ new__都会调用apps.register_model，它会在all_models中创建一个条目。 所有导入的模型都已注册，无论它们是否已在已安装的应用程序中定义，以及是否已填充注册表。 由于无法安全地重新导入模块（它可以重新执行初始化代码），因此永远不会覆盖或重置all_models。
        '''
        self.all_models = defaultdict(OrderedDict)

        # 将标签映射到已安装应用程序的AppConfig实例。
        self.app_configs = OrderedDict()

        # adp_configs堆栈。 用于在set_available_apps和set_installed_apps中存储当前状态。
        self.stored_app_configs = []

        # 是否填充了注册表。
        self.apps_ready = self.models_ready = self.ready = False

        # 锁定线程安全的population.。
        self._lock = threading.RLock()
        self.loading = False

        # 映射（“app_label”，“modelname”）元组到相应模型准备就绪时要调用的函数列表。 由此类的`lazy_model_operation（）`和`do_pending_operations（）`方法使用。
        self._pending_operations = defaultdict(list)

        # 填充应用程序和模型，除非它是主注册表。
        if installed_apps is not None:
            self.populate(installed_apps)

    def populate(self, installed_apps=None):
        """
        加载应用程序配置和模型。

        导入每个应用程序模块，然后导入每个模型

        它是线程安全且幂等的，但不是可重入的。
        """
        if self.ready:
            return

        # populate（）可能由两个线程并行调用，在初始化WSGI可调用之前创建线程的服务器上。
        with self._lock:
            if self.ready:
                return

            # RLock阻止其他线程进入此部分。 下面的比较和设置操作是原子的。
            if self.loading:
                # 防止可重入调用以避免两次运行AppConfig.ready（）方法。
                raise RuntimeError("populate() isn't reentrant")
            self.loading = True

            # 阶段1：初始化应用程序配置并导入应用程序模块。
            for entry in installed_apps:
                app_config = entry if isinstance(entry, AppConfig) else AppConfig.create(entry)
                if app_config.label in self.app_configs:
                    raise ImproperlyConfigured(
                        "Application labels aren't unique, "
                        "duplicates: %s" % app_config.label)

                self.app_configs[app_config.label] = app_config
                app_config.apps = self

            # 检查重复的应用名称。
            counts = Counter(
                app_config.name for app_config in self.app_configs.values())
            if duplicates := [
                name for name, count in counts.most_common() if count > 1
            ]:
                raise ImproperlyConfigured(
                    "Application names aren't unique, "
                    "duplicates: %s" % ", ".join(duplicates))

            self.apps_ready = True

            # 阶段2：导入模型模块。
            for app_config in self.app_configs.values():
                app_config.import_models()

            self.clear_cache()

            self.models_ready = True

            # 阶段3：运行app配置的ready（）方法。
            for app_config in self.get_app_configs():
                app_config.ready()

            self.ready = True

    def check_apps_ready(self):
        """如果尚未导入所有应用程序，则引发异常。"""
        if not self.apps_ready:
            from django.conf import settings
            # 如果“not ready”是由于未配置的设置，则访问INSTALLED_APPS会引发一个更有用的ImproperlyConfigured异常。
            settings.INSTALLED_APPS
            raise AppRegistryNotReady("Apps aren't loaded yet.")

    def check_models_ready(self):
        """如果尚未导入所有模型，则引发异常。"""
        if not self.models_ready:
            raise AppRegistryNotReady("Models aren't loaded yet.")

    def get_app_configs(self):
        """导入应用程序并返回可迭代的app配置。"""
        self.check_apps_ready()
        return self.app_configs.values()

    def get_app_config(self, app_label):
        """
        导入应用程序并返回给定标签的应用程序配置。

        如果此标签不存在应用程序，则引发LookupError。
        """
        self.check_apps_ready()
        try:
            return self.app_configs[app_label]
        except KeyError:
            message = "No installed app with label '%s'." % app_label
            for app_config in self.get_app_configs():
                if app_config.name == app_label:
                    message += " Did you mean '%s'?" % app_config.label
                    break
            raise LookupError(message)

    # 至少对于Django的测试套件，这种方法至关重要。
    @functools.lru_cache(maxsize=None)
    def get_models(self, include_auto_created=False, include_swapped=False):
        """
        返回所有已安装模型的列表。

         默认情况下，不包括以下模型：

          - 无需多对多关系的自动创建模型 一个明确的中间表，
          - 已换掉的model。

         将相应的关键字参数设置为True以包含此类模型。
        """
        self.check_models_ready()

        result = []
        for app_config in self.app_configs.values():
            result.extend(list(app_config.get_models(include_auto_created, include_swapped)))
        return result

    def get_model(self, app_label, model_name=None, require_ready=True):
        """
        返回与给定app_label和model_name匹配的模型。

        作为快捷方式，app_label可以采用<app_label>。<model_name>的形式。 model_name不区分大小写。

        如果此标签不存在应用程序，则引发LookupError，或者在应用程序中不存在具有此名称的模型。 如果使用不包含一个点的单个参数调用，则引发ValueError。
        """
        if require_ready:
            self.check_models_ready()
        else:
            self.check_apps_ready()

        if model_name is None:
            app_label, model_name = app_label.split('.')

        app_config = self.get_app_config(app_label)

        if not require_ready and app_config.models is None:
            app_config.import_models()

        return app_config.get_model(model_name, require_ready=require_ready)

    def register_model(self, app_label, model):
        # 由于在导入模型时调用此方法，因为存在导入循环的风险，因此无法执行导入。 它不能调用get_app_config（）。
        model_name = model._meta.model_name
        app_models = self.all_models[app_label]
        if model_name in app_models:
            if (model.__name__ == app_models[model_name].__name__ and
                    model.__module__ == app_models[model_name].__module__):
                warnings.warn(
                    "Model '%s.%s' was already registered. "
                    "Reloading models is not advised as it can lead to inconsistencies, "
                    "most notably with related models." % (app_label, model_name),
                    RuntimeWarning, stacklevel=2)
            else:
                raise RuntimeError(
                    "Conflicting '%s' models in application '%s': %s and %s." %
                    (model_name, app_label, app_models[model_name], model))
        app_models[model_name] = model
        self.do_pending_operations(model)
        self.clear_cache()

    def is_installed(self, app_name):
        """
        检查注册表中是否存在具有此名称的应用程序。

        app_name是应用的全名，例如'django.contrib.admin'。
        """
        self.check_apps_ready()
        return any(ac.name == app_name for ac in self.app_configs.values())

    def get_containing_app_config(self, object_name):
        """
        查找包含给定对象的应用程序配置。

        object_name是对象的dotted Python路径。

        在嵌套的情况下，返回内部应用程序的app配置。
        如果对象不在任何已注册的应用程序配置中，则返回None。
        """
        self.check_apps_ready()
        candidates = []
        for app_config in self.app_configs.values():
            if object_name.startswith(app_config.name):
                subpath = object_name[len(app_config.name):]
                if subpath == '' or subpath[0] == '.':
                    candidates.append(app_config)
        if candidates:
            return sorted(candidates, key=lambda ac: -len(ac.name))[0]

    def get_registered_model(self, app_label, model_name):
        """
        与get_model（）类似，但不要求应用程序与给定的app_label一起存在。

        即使在填充注册表时，在导入时调用此方法也是安全的。
        """
        model = self.all_models[app_label].get(model_name.lower())
        if model is None:
            raise LookupError(
                "Model '%s.%s' not registered." % (app_label, model_name))
        return model

    @functools.lru_cache(maxsize=None)
    def get_swappable_settings_name(self, to_string):
        """
        对于给定的模型字符串（例如“auth.User”），如果它引用可交换模型，则返回相应设置名称的名称。 如果引用的模型不可交换，则返回None。

         此方法使用lru_cache进行修饰，因为它在迁移时性能至关重要。 由于Django加载设置后交换设置不会改变，因此没有理由一遍又一遍地获取相应的设置属性。
        """
        for model in self.get_models(include_swapped=True):
            swapped = model._meta.swapped
            # 这个模型是否换成了to_string给出的模型？
            if swapped and swapped == to_string:
                return model._meta.swappable
            # 这个模型是可交换的还是to_string给出的模型？
            if model._meta.swappable and model._meta.label == to_string:
                return model._meta.swappable
        return None

    def set_available_apps(self, available):
        """
        限制get_app_config [s]使用的已安装应用程序集。

        available必须是可迭代的应用程序名称。

        set_available_apps（）必须与unset_available_apps（）平衡。

        主要用于TransactionTestCase中的性能优化。

        这种方法在不触发任何导入的意义上是安全的。
        """
        available = set(available)
        installed = {app_config.name for app_config in self.get_app_configs()}
        if not available.issubset(installed):
            raise ValueError(
                "Available apps isn't a subset of installed apps, extra apps: %s"
                % ", ".join(available - installed)
            )

        self.stored_app_configs.append(self.app_configs)
        self.app_configs = OrderedDict(
            (label, app_config)
            for label, app_config in self.app_configs.items()
            if app_config.name in available)
        self.clear_cache()

    def unset_available_apps(self):
        """取消之前对set_available_apps（）的调用。"""
        self.app_configs = self.stored_app_configs.pop()
        self.clear_cache()

    def set_installed_apps(self, installed):
        """
        为get_app_config [s]启用一组不同的已安装应用程序。

        安装必须是与INSTALLED_APPS格式相同的可迭代。

        set_installed_apps（）必须与unset_installed_apps（）保持平衡，即使它以异常退出也是如此。

        主要用作测试中setting_changed信号的接收器。

        此方法可能会触发新导入，这可能会将新模型添加到所有导入模型的注册表中。 即使在unset_installed_apps（）之后，它们仍将保留在注册表中。 由于无法安全地重放导入（例如，可能导致两次注册侦听器），因此模型在导入时会被注册，并且永远不会被删除。
        """
        if not self.ready:
            raise AppRegistryNotReady("App registry isn't ready yet.")
        self.stored_app_configs.append(self.app_configs)
        self.app_configs = OrderedDict()
        self.apps_ready = self.models_ready = self.loading = self.ready = False
        self.clear_cache()
        self.populate(installed)

    def unset_installed_apps(self):
        """取消之前对set_installed_apps（）的调用。"""
        self.app_configs = self.stored_app_configs.pop()
        self.apps_ready = self.models_ready = self.ready = True
        self.clear_cache()

    def clear_cache(self):
        """
        清除所有内部缓存，用于更改app注册表的方法。

         这主要用于测试。
        """
        # 在每个模型上调用expire cache。 这将清除关系树和字段缓存。
        self.get_models.cache_clear()
        if self.ready:
            # 绕过self.get_models（）以防止重新填充缓存。
            # 这特别可以防止在克隆时缓存空值。
            for app_config in self.app_configs.values():
                for model in app_config.get_models(include_auto_created=True):
                    model._meta._expire_cache()

    def lazy_model_operation(self, function, *model_keys):
        """
        获取一个函数和一些（“app_label”，“modelname”）元组，并且在导入和注册所有相应模型后，使用模型类作为参数调用该函数。

         传递给此方法的函数必须接受n个模型作为参数，其中n = len（model_keys）。
        """
        # Base case：没有参数，只需执行该函数。
        if not model_keys:
            function()
        # 递归情况：取model_keys的头，等待导入和注册相应的模型类，然后将该参数应用于提供的函数。 将生成的部分传递给lazy_model_operation（）以及剩余的模型args并重复，直到加载所有模型并应用所有参数。
        else:
            next_model, more_models = model_keys[0], model_keys[1:]

            # 这将在导入和注册与next_model相对应的类之后执行。 `func`属性提供与partials的duck-type兼容性。
            def apply_next_model(model):
                next_function = partial(apply_next_model.func, model)
                self.lazy_model_operation(next_function, *more_models)
            apply_next_model.func = function

            # 如果已导入并注册了模型，请立即将其部分应用于该功能。 如果没有，请将其添加到模型的待处理操作列表中，一旦模型准备就绪，将以模型类作为其唯一参数执行。
            try:
                model_class = self.get_registered_model(*next_model)
            except LookupError:
                self._pending_operations[next_model].append(apply_next_model)
            else:
                apply_next_model(model_class)

    def do_pending_operations(self, model):
        """
        拿一个新准备的模型并将其传递给等待它的每个函数。 这在Apps.register_model（）的最后调用。
        """
        key = model._meta.app_label, model._meta.model_name
        for function in self._pending_operations.pop(key, []):
            function(model)


apps = Apps(installed_apps=None)
