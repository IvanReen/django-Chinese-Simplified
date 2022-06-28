import functools

from django.conf import settings
from django.urls import LocalePrefixPattern, URLResolver, get_resolver, path
from django.views.i18n import set_language


def i18n_patterns(*urls, prefix_default_language=True):
    """
    将语言代码前缀添加到此函数中的每个URL模式。
    这可能只在根URLconf中使用，而不是在包含的URLconf中使用。
    """
    return (
        [
            URLResolver(
                LocalePrefixPattern(
                    prefix_default_language=prefix_default_language
                ),
                list(urls),
            )
        ]
        if settings.USE_I18N
        else list(urls)
    )


@functools.lru_cache(maxsize=None)
def is_language_prefix_patterns_used(urlconf):
    """
    返回两个布尔元组：（
         如果在URLconf中使用了i18n_patterns（）（LocalePrefixPattern），则为“True”，
         如果默认语言应该加前缀，则为“True”
    ）
    """
    return next(
        (
            (True, url_pattern.pattern.prefix_default_language)
            for url_pattern in get_resolver(urlconf).url_patterns
            if isinstance(url_pattern.pattern, LocalePrefixPattern)
        ),
        (False, False),
    )


urlpatterns = [
    path('setlang/', set_language, name='set_language'),
]
