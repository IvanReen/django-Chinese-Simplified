import os
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import module_has_submodule

MODELS_MODULE_NAME = 'models'


class AppConfig:
    """表示Django应用程序及其配置的类。"""

    def __init__(self, app_name, app_module):
        # 应用程序的完整Python路径，例如'django.contrib.admin'。
        self.name = app_name

        # 用于应用的根模块，例如 <module'django.contrib.admin' from 'django/contrib/admin/__init__.py'>.
        self.module = app_module

        # 引用包含此AppConfig的Apps注册表。 在注册AppConfig实例时由注册表设置。
        self.apps = None

        # 可以在子类中的类级别定义以下属性，因此是测试和设置模式。

        # 应用程序的Python路径的最后一个组件，例如“admin”。 这个值在Django项目中必须是唯一的。
        if not hasattr(self, 'label'):
            self.label = app_name.rpartition(".")[2]

        # 应用程序的人类可读名称，例如“Admin”。
        if not hasattr(self, 'verbose_name'):
            self.verbose_name = self.label.title()

        # 应用程序目录的文件系统路径，例如 '/path/to/django/contrib/admin'.
        if not hasattr(self, 'path'):
            self.path = self._path_from_module(app_module)

        # 包含模型的模块 来自'django / contrib / admin / models.py'>的<module'django.contrib.admin.models'。 由import_models（）设置。 如果应用程序没有模型模块，则为无。
        self.models_module = None

        # 将小写模型名称映射到模型类。 最初设置为None以防止在import_models（）运行之前意外访问。
        self.models = None

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.label)

    def _path_from_module(self, module):
        """尝试从其模块确定应用程序的文件系统路径。"""
        # 有关此方法在各种情况下的行为的扩展讨论，请参阅＃21874。
        # 将路径转换为列表，因为Python的_NamespacePath不支持索引。
        paths = list(getattr(module, '__path__', []))
        if len(paths) != 1:
            filename = getattr(module, '__file__', None)
            if filename is not None:
                paths = [os.path.dirname(filename)]
            else:
                # 由于未知原因，有时__path__返回的列表包含必须删除的重复项（＃25246）。
                paths = list(set(paths))
        if len(paths) > 1:
            raise ImproperlyConfigured(
                "The app module %r has multiple filesystem locations (%r); "
                "you must configure this app with an AppConfig subclass "
                "with a 'path' class attribute." % (module, paths))
        elif not paths:
            raise ImproperlyConfigured(
                "The app module %r has no filesystem location, "
                "you must configure this app with an AppConfig subclass "
                "with a 'path' class attribute." % (module,))
        return paths[0]

    @classmethod
    def create(cls, entry):
        """
        从INSTALLED_APPS中的条目创建应用程序配置的工厂。
        """
        try:
            # 如果import_module成功，则entry是app模块的路径，可以使用default_app_config指定app配置类。 否则，entry是app config类的路径或错误。
            module = import_module(entry)

        except ImportError:
            # 跟踪导入为app模块失败。 如果作为app配置类导入也失败，我们将再次触发ImportError。
            module = None

            mod_path, _, cls_name = entry.rpartition('.')

            # 当条目不能是app配置类的路径时，引发原始异常。
            if not mod_path:
                raise

        else:
            try:
                # 如果这样可行，则app模块指定应用程序配置类。
                entry = module.default_app_config
            except AttributeError:
                # 否则，它只使用默认的app config类。
                return cls(entry, module)
            else:
                mod_path, _, cls_name = entry.rpartition('.')

        # 如果我们达到这一点，我们必须尝试加载位于<mod_path>的app配置类。<cls_name>
        mod = import_module(mod_path)
        try:
            cls = getattr(mod, cls_name)
        except AttributeError:
            if module is None:
                # 如果作为应用程序模块导入失败，则该错误可能包含最具信息性的回溯。 再次触发它。
                import_module(entry)
            else:
                raise

        # 检查明显的错误。 （此检查可防止鸭子typing，但如果在实践中成为问题，则可以将其删除。）
        if not issubclass(cls, AppConfig):
            raise ImproperlyConfigured(
                "'%s' isn't a subclass of AppConfig." % entry)

        # 在此处获取应用程序名称，而不是在AppClass .__ init__中，以便在一个位置保留对INSTALLED_APPS中的条目的所有错误检查。
        try:
            app_name = cls.name
        except AttributeError:
            raise ImproperlyConfigured(
                "'%s' must supply a name attribute." % entry)

        # 确保app_name指向有效模块。
        try:
            app_module = import_module(app_name)
        except ImportError:
            raise ImproperlyConfigured(
                "Cannot import '%s'. Check that '%s.%s.name' is correct." % (
                    app_name, mod_path, cls_name,
                )
            )

        # return app配置类的路径。
        return cls(app_name, app_module)

    def get_model(self, model_name, require_ready=True):
        """
        使用给定的不区分大小写的model_name返回模型。

        如果不存在具有此名称的模型，则引发LookupError。
        """
        if require_ready:
            self.apps.check_models_ready()
        else:
            self.apps.check_apps_ready()
        try:
            return self.models[model_name.lower()]
        except KeyError:
            raise LookupError(
                "App '%s' doesn't have a '%s' model." % (self.label, model_name))

    def get_models(self, include_auto_created=False, include_swapped=False):
        """
        返回一个可迭代的模型。

        默认情况下，不包括以下模型：

        - 自动创建的多对多关系模型，没有明确的中间表，
        - 已换掉的型号。

        将相应的关键字参数设置为True以包含此类模型。
        关键字参数没有记录; 它们是私有API。
        """
        self.apps.check_models_ready()
        for model in self.models.values():
            if model._meta.auto_created and not include_auto_created:
                continue
            if model._meta.swapped and not include_swapped:
                continue
            yield model

    def import_models(self):
        # 此应用程序的模型字典，主要维护在此AppConfig附加到的应用程序的“all_models”属性中。
        self.models = self.apps.all_models[self.label]

        if module_has_submodule(self.module, MODELS_MODULE_NAME):
            models_module_name = '%s.%s' % (self.name, MODELS_MODULE_NAME)
            self.models_module = import_module(models_module_name)

    def ready(self):
        """
        在子类中重写此方法以在Django启动时运行代码。
        """
