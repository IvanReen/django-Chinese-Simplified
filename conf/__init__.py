"""
Django的设置和配置。

从DJANGO_SETTINGS_MODULE环境变量指定的模块读取值，然后从django.conf.global_settings读取; 请参阅global_settings.py以获取所有可能变量的列表。
"""

import importlib
import os
import time
import warnings
from pathlib import Path

from django.conf import global_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import RemovedInDjango30Warning
from django.utils.functional import LazyObject, empty

ENVIRONMENT_VARIABLE = "DJANGO_SETTINGS_MODULE"


class LazySettings(LazyObject):
    """
    全局Django设置或自定义设置对象的惰性代理。 用户可以在使用之前手动配置设置。 否则，Django使用DJANGO_SETTINGS_MODULE指向的设置模块。
    """
    def _setup(self, name=None):
        """
        加载环境变量指向的设置模块。 如果用户尚未手动配置设置，则在首次使用设置时使用此选项。
        """
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        if not settings_module:
            desc = ("setting %s" % name) if name else "settings"
            raise ImproperlyConfigured(
                "Requested %s, but settings are not configured. "
                "You must either define the environment variable %s "
                "or call settings.configure() before accessing settings."
                % (desc, ENVIRONMENT_VARIABLE))

        self._wrapped = Settings(settings_module)

    def __repr__(self):
        # 对类名进行硬编码，否则会生成“Settings”。
        if self._wrapped is empty:
            return '<LazySettings [Unevaluated]>'
        return '<LazySettings "%(settings_module)s">' % {
            'settings_module': self._wrapped.SETTINGS_MODULE,
        }

    def __getattr__(self, name):
        """返回设置的值并将其缓存在self .__ dict__中。"""
        if self._wrapped is empty:
            self._setup(name)
        val = getattr(self._wrapped, name)
        self.__dict__[name] = val
        return val

    def __setattr__(self, name, value):
        """
        设置设置值。 如果_wrapped更改（@override_settings执行此操作）或清除设置的单个值，则清除所有缓存的值。
        """
        if name == '_wrapped':
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        """删除设置并根据需要从缓存中清除它。"""
        super().__delattr__(name)
        self.__dict__.pop(name, None)

    def configure(self, default_settings=global_settings, **options):
        """
        被叫手动配置设置。 'default_settings'参数设置从哪里检索任何未指定的值（其参数必须支持属性访问（__getattr __））。
        """
        if self._wrapped is not empty:
            raise RuntimeError('Settings already configured.')
        holder = UserSettingsHolder(default_settings)
        for name, value in options.items():
            setattr(holder, name, value)
        self._wrapped = holder

    @property
    def configured(self):
        """如果已配置设置，则返回True。"""
        return self._wrapped is not empty


class Settings:
    def __init__(self, settings_module):
        # 从全局设置更新此dict（但仅适用于ALL_CAPS设置）
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        # 存储设置模块，以防有人后来 cares
        self.SETTINGS_MODULE = settings_module

        mod = importlib.import_module(self.SETTINGS_MODULE)

        tuple_settings = (
            "INSTALLED_APPS",
            "TEMPLATE_DIRS",
            "LOCALE_PATHS",
        )
        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                if (setting in tuple_settings and
                        not isinstance(setting_value, (list, tuple))):
                    raise ImproperlyConfigured("The %s setting must be a list or a tuple. " % setting)
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

        if not self.SECRET_KEY:
            raise ImproperlyConfigured("The SECRET_KEY setting must not be empty.")

        if self.is_overridden('DEFAULT_CONTENT_TYPE'):
            warnings.warn('The DEFAULT_CONTENT_TYPE setting is deprecated.', RemovedInDjango30Warning)

        if hasattr(time, 'tzset') and self.TIME_ZONE:
            # 我们可以，尝试验证时区。 如果我们找不到这个文件，就不会发生检查，这是无害的。
            zoneinfo_root = Path('/usr/share/zoneinfo')
            zone_info_file = zoneinfo_root.joinpath(*self.TIME_ZONE.split('/'))
            if zoneinfo_root.exists() and not zone_info_file.exists():
                raise ValueError("Incorrect timezone setting: %s" % self.TIME_ZONE)
            # 将时区信息移动到os.environ中。 请参阅＃2315票，了解我们为什么不无条件地执行此操作（breaks Windows）。
            os.environ['TZ'] = self.TIME_ZONE
            time.tzset()

    def is_overridden(self, setting):
        return setting in self._explicit_settings

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            'cls': self.__class__.__name__,
            'settings_module': self.SETTINGS_MODULE,
        }


class UserSettingsHolder:
    """用户配置设置的持有者。"""
    # SETTINGS_MODULE在手动配置（独立）的情况下没有多大意义。
    SETTINGS_MODULE = None

    def __init__(self, default_settings):
        """
        从default_settings中指定的模块（如果可能）满足不在此类中的配置变量的请求。
        """
        self.__dict__['_deleted'] = set()
        self.default_settings = default_settings

    def __getattr__(self, name):
        if name in self._deleted:
            raise AttributeError
        return getattr(self.default_settings, name)

    def __setattr__(self, name, value):
        self._deleted.discard(name)
        if name == 'DEFAULT_CONTENT_TYPE':
            warnings.warn('The DEFAULT_CONTENT_TYPE setting is deprecated.', RemovedInDjango30Warning)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        self._deleted.add(name)
        if hasattr(self, name):
            super().__delattr__(name)

    def __dir__(self):
        return sorted(
            s for s in list(self.__dict__) + dir(self.default_settings)
            if s not in self._deleted
        )

    def is_overridden(self, setting):
        deleted = (setting in self._deleted)
        set_locally = (setting in self.__dict__)
        set_on_default = getattr(self.default_settings, 'is_overridden', lambda s: False)(setting)
        return deleted or set_locally or set_on_default

    def __repr__(self):
        return '<%(cls)s>' % {
            'cls': self.__class__.__name__,
        }


settings = LazySettings()
