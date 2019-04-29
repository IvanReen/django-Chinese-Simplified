from django.apps import AppConfig
from django.contrib.admin.checks import check_admin_app, check_dependencies
from django.core import checks
from django.utils.translation import gettext_lazy as _


class SimpleAdminConfig(AppConfig):
    """简单的AppConfig，不进行自动发现。"""

    default_site = 'django.contrib.admin.sites.AdminSite'
    name = 'django.contrib.admin'
    verbose_name = _("Administration")

    def ready(self):
        checks.register(check_dependencies, checks.Tags.admin)
        checks.register(check_admin_app, checks.Tags.admin)


class AdminConfig(SimpleAdminConfig):
    """管理员的默认AppConfig执行自动发现。"""

    def ready(self):
        super().ready()
        self.module.autodiscover()
