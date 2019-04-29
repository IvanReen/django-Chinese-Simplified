import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import re_path
from django.views.static import serve


def static(prefix, view=serve, **kwargs):
    """
    在调试模式下返回服务文件的URL模式。

    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns = [
        # ...你的其他URLconf就在这里......
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    """
    if not prefix:
        raise ImproperlyConfigured("Empty static prefix not permitted")
    elif not settings.DEBUG or '://' in prefix:
        # 如果不处于调试模式或非本地前缀，则为no-op。
        return []
    return [
        re_path(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), view, kwargs=kwargs),
    ]
