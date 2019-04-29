"""
默认的Django设置。 使用DJANGO_SETTINGS_MODULE环境变量指向的模块中的设置覆盖这些设置。
"""


# 这里定义为do-nothing函数，因为我们无法导入django.utils.translation  - 该模块取决于设置。
def gettext_noop(s):
    return s


####################
# CORE             #
####################

DEBUG = False

# 框架是否应该传播原始异常而不是捕获它们。 这在某些测试情况下很有用，不应在实际站点上使用。
DEBUG_PROPAGATE_EXCEPTIONS = False

# 获得代码错误通知的人。格式为 [('Full Name', 'email@example.com'), ('Full Name', 'anotheremail@example.com')]
ADMINS = []

# 作为字符串的IP地址列表：
# *当DEBUG为true时，请参阅调试注释
# *接收x-headers
INTERNAL_IPS = []

# 对此站点有效的主机/域名。
# “*”匹配任何内容，“。example.com”匹配example.com和所有子域
ALLOWED_HOSTS = []

# 此安装的本地时区。 所有选择都可以在这里找到：https：//en.wikipedia.org/wiki/List_of_tz_zones_by_name（虽然并非所有系统都支持所有可能性）。 当USE_TZ为True时，将其解释为默认用户时区。
TIME_ZONE = 'America/Chicago'

# 如果将其设置为True，Django将使用时区感知日期时间。
USE_TZ = False

# 此安装的语言代码。 所有选择都可以在这里找到： http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# 我们提供的语言，开箱即用。
LANGUAGES = [
    ('af', gettext_noop('Afrikaans')),
    ('ar', gettext_noop('Arabic')),
    ('ast', gettext_noop('Asturian')),
    ('az', gettext_noop('Azerbaijani')),
    ('bg', gettext_noop('Bulgarian')),
    ('be', gettext_noop('Belarusian')),
    ('bn', gettext_noop('Bengali')),
    ('br', gettext_noop('Breton')),
    ('bs', gettext_noop('Bosnian')),
    ('ca', gettext_noop('Catalan')),
    ('cs', gettext_noop('Czech')),
    ('cy', gettext_noop('Welsh')),
    ('da', gettext_noop('Danish')),
    ('de', gettext_noop('German')),
    ('dsb', gettext_noop('Lower Sorbian')),
    ('el', gettext_noop('Greek')),
    ('en', gettext_noop('English')),
    ('en-au', gettext_noop('Australian English')),
    ('en-gb', gettext_noop('British English')),
    ('eo', gettext_noop('Esperanto')),
    ('es', gettext_noop('Spanish')),
    ('es-ar', gettext_noop('Argentinian Spanish')),
    ('es-co', gettext_noop('Colombian Spanish')),
    ('es-mx', gettext_noop('Mexican Spanish')),
    ('es-ni', gettext_noop('Nicaraguan Spanish')),
    ('es-ve', gettext_noop('Venezuelan Spanish')),
    ('et', gettext_noop('Estonian')),
    ('eu', gettext_noop('Basque')),
    ('fa', gettext_noop('Persian')),
    ('fi', gettext_noop('Finnish')),
    ('fr', gettext_noop('French')),
    ('fy', gettext_noop('Frisian')),
    ('ga', gettext_noop('Irish')),
    ('gd', gettext_noop('Scottish Gaelic')),
    ('gl', gettext_noop('Galician')),
    ('he', gettext_noop('Hebrew')),
    ('hi', gettext_noop('Hindi')),
    ('hr', gettext_noop('Croatian')),
    ('hsb', gettext_noop('Upper Sorbian')),
    ('hu', gettext_noop('Hungarian')),
    ('ia', gettext_noop('Interlingua')),
    ('id', gettext_noop('Indonesian')),
    ('io', gettext_noop('Ido')),
    ('is', gettext_noop('Icelandic')),
    ('it', gettext_noop('Italian')),
    ('ja', gettext_noop('Japanese')),
    ('ka', gettext_noop('Georgian')),
    ('kab', gettext_noop('Kabyle')),
    ('kk', gettext_noop('Kazakh')),
    ('km', gettext_noop('Khmer')),
    ('kn', gettext_noop('Kannada')),
    ('ko', gettext_noop('Korean')),
    ('lb', gettext_noop('Luxembourgish')),
    ('lt', gettext_noop('Lithuanian')),
    ('lv', gettext_noop('Latvian')),
    ('mk', gettext_noop('Macedonian')),
    ('ml', gettext_noop('Malayalam')),
    ('mn', gettext_noop('Mongolian')),
    ('mr', gettext_noop('Marathi')),
    ('my', gettext_noop('Burmese')),
    ('nb', gettext_noop('Norwegian Bokmål')),
    ('ne', gettext_noop('Nepali')),
    ('nl', gettext_noop('Dutch')),
    ('nn', gettext_noop('Norwegian Nynorsk')),
    ('os', gettext_noop('Ossetic')),
    ('pa', gettext_noop('Punjabi')),
    ('pl', gettext_noop('Polish')),
    ('pt', gettext_noop('Portuguese')),
    ('pt-br', gettext_noop('Brazilian Portuguese')),
    ('ro', gettext_noop('Romanian')),
    ('ru', gettext_noop('Russian')),
    ('sk', gettext_noop('Slovak')),
    ('sl', gettext_noop('Slovenian')),
    ('sq', gettext_noop('Albanian')),
    ('sr', gettext_noop('Serbian')),
    ('sr-latn', gettext_noop('Serbian Latin')),
    ('sv', gettext_noop('Swedish')),
    ('sw', gettext_noop('Swahili')),
    ('ta', gettext_noop('Tamil')),
    ('te', gettext_noop('Telugu')),
    ('th', gettext_noop('Thai')),
    ('tr', gettext_noop('Turkish')),
    ('tt', gettext_noop('Tatar')),
    ('udm', gettext_noop('Udmurt')),
    ('uk', gettext_noop('Ukrainian')),
    ('ur', gettext_noop('Urdu')),
    ('vi', gettext_noop('Vietnamese')),
    ('zh-hans', gettext_noop('Simplified Chinese')),
    ('zh-hant', gettext_noop('Traditional Chinese')),
]

# 使用BiDi（从右到左）布局的语言
LANGUAGES_BIDI = ["he", "ar", "fa", "ur"]

# 如果将其设置为False，Django将进行一些优化，以免加载国际化机制。
USE_I18N = True
LOCALE_PATHS = []

# 语言cookie的设置
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = None
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_PATH = '/'


# 如果将此设置为True，Django将根据用户当前区域设置格式化日期，数字和日历。
USE_L10N = False

# 该网站不一定是技术经理。 他们会收到损坏的链接通知和其他各种电子邮件。
MANAGERS = ADMINS

# 如果未手动指定MIME类型，则用于所有HttpResponse对象的默认内容类型和字符集。 这些用于构造Content-Type标头。
DEFAULT_CONTENT_TYPE = 'text/html'
DEFAULT_CHARSET = 'utf-8'

# 从磁盘读取的文件的编码（模板和初始SQL文件）。
FILE_CHARSET = 'utf-8'

# 错误消息来自的电子邮件地址。
SERVER_EMAIL = 'root@localhost'

# 数据库连接信息。 如果留空，则默认为虚拟后端。
DATABASES = {}

# 用于实现数据库路由行为的类。
DATABASE_ROUTERS = []

# 要使用的电子邮件后端。 有关可能的快捷方式，请参阅django.core.mail。
# 默认使用SMTP后端。
# 可以通过提供定义EmailBackend类的模块的Python路径来指定第三方后端。
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# 主持人发送电子邮件。
EMAIL_HOST = 'localhost'

# 发送电子邮件的端口。
EMAIL_PORT = 25

# 是否在本地时区或UTC中发送SMTP“日期”标头。
EMAIL_USE_LOCALTIME = False

# EMAIL_HOST的可选SMTP身份验证信息。
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None

# 表示已安装应用的字符串列表。
INSTALLED_APPS = []

TEMPLATES = []

# 默认表单呈现类。
FORM_RENDERER = 'django.forms.renderers.DjangoTemplates'

# 用于站点管理员的各种自动通信的默认电子邮件地址。
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# 使用django.core.mail.mail_admins或... mail_managers发送电子邮件的主题行前缀。 确保包含尾随空格。
EMAIL_SUBJECT_PREFIX = '[Django] '

# 是否在URL中附加尾部斜杠。
APPEND_SLASH = True

# 是否预先添加“www。” 子域到没有它的URL。
PREPEND_WWW = False

# 覆盖SCRIPT_NAME的服务器派生值
FORCE_SCRIPT_NAME = None

# 在系统范围内表示不允许访问任何页面的User-Agent字符串的已编译正则表达式对象的列表。 用于坏机器人/爬虫。 这里有一些例子：
#     import re
#     DISALLOWED_USER_AGENTS = [
#         re.compile(r'^NaverBot.*'),
#         re.compile(r'^EmailSiphon.*'),
#         re.compile(r'^SiteSucker.*'),
#         re.compile(r'^sohu-search'),
#     ]
DISALLOWED_USER_AGENTS = []

ABSOLUTE_URL_OVERRIDES = {}

# 已编译的正则表达式对象列表，表示BrokenLinkEmailsMiddleware无需报告的URL。 这里有一些例子：
#    import re
#    IGNORABLE_404_URLS = [
#        re.compile(r'^/apple-touch-icon.*\.png$'),
#        re.compile(r'^/favicon.ico$'),
#        re.compile(r'^/robots.txt$'),
#        re.compile(r'^/phpmyadmin/'),
#        re.compile(r'\.(cgi|php|pl)$'),
#    ]
IGNORABLE_404_URLS = []

# 这个特殊Django安装的密钥。 用于密钥散列算法。 在你的设置中设置它，或Django会大声抱怨。
SECRET_KEY = ''

# 保存媒体的默认文件存储机制。
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# 用于保存用户上载文件的目录的绝对文件系统路径。
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# 处理从MEDIA_ROOT提供的媒体的URL。
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# 应收集目录静态文件的绝对路径。
# Example: "/var/www/example.com/static/"
STATIC_ROOT = None

# 处理从STATIC_ROOT提供的静态文件的URL。
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = None

# 要按顺序应用的上载处理程序类的列表。
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# 请求在流入文件系统而不是内存之前的最大大小（以字节为单位）。
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # i.e. 2.5 MB

# 在引发SuspiciousOperation（RequestDataTooBig）之前将读取的请求数据（不包括文件上载）的最大字节数。
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # i.e. 2.5 MB

# 在引发SuspiciousOperation（TooManyFieldsSent）之前将读取的最大GET / POST参数数。
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# 将临时保存上载流文件的目录。 值为“None”将使Django使用操作系统的默认临时目录（即* nix系统上的“/ tmp”）。
FILE_UPLOAD_TEMP_DIR = None

# 用于设置新上传文件的数字模式。 该值应该是您直接传递给os.chmod的模式; 请参阅https://docs.python.org/3/library/os.html#files-and-directories。
FILE_UPLOAD_PERMISSIONS = None

# 上传文件时分配给新创建的目录的数字模式。 当你传递给os.chmod时，该值应该是一个模式; 请参阅https://docs.python.org/3/library/os.html#files-and-directories。
FILE_UPLOAD_DIRECTORY_PERMISSIONS = None

# 用户将放置自定义格式定义的Python模块路径。 此设置指向的目录应包含名为locales的子目录，其中包含formats.py文件（即myproject / locale / en / formats.py等的“myproject.locale”使用）
FORMAT_MODULE_PATH = None

# 日期对象的默认格式。 查看所有可用的格式字符串：
# http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
DATE_FORMAT = 'N j, Y'

# datetime对象的默认格式。 查看所有可用的格式字符串：
# http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
DATETIME_FORMAT = 'N j, Y, P'

# 时间对象的默认格式。 查看所有可用的格式字符串：
# http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
TIME_FORMAT = 'P'

# 仅当年份和月份相关时，日期对象的默认格式。 查看所有可用的格式字符串：
# http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
YEAR_MONTH_FORMAT = 'F Y'

# 仅当月份和日期相关时，日期对象的默认格式。 查看所有可用的格式字符串：
# http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
MONTH_DAY_FORMAT = 'F j'

# 日期对象的默认短格式。 查看所有可用的格式字符串：
# http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
SHORT_DATE_FORMAT = 'm/d/Y'

# datetime对象的默认短格式。 查看所有可用的格式字符串：
# http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
SHORT_DATETIME_FORMAT = 'm/d/Y P'

# 从输入框解析日期时要使用的默认格式，按顺序查看所有可用的格式字符串：
# http://docs.python.org/library/datetime.html#strftime-behavior
# *请注意，这些格式字符串与显示日期的字符串不同
DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',  # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',             # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',             # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',             # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',             # '25 October 2006', '25 October, 2006'
]

# 从输入框解析时间时要使用的默认格式，按顺序查看所有可用的格式字符串：
# http://docs.python.org/library/datetime.html#strftime-behavior
# *请注意，这些格式字符串与显示日期的字符串不同
TIME_INPUT_FORMATS = [
    '%H:%M:%S',     # '14:30:59'
    '%H:%M:%S.%f',  # '14:30:59.000200'
    '%H:%M',        # '14:30'
]

# 从输入框解析日期和时间时要使用的默认格式，按顺序在此处查看所有可用的格式字符串：
# http://docs.python.org/library/datetime.html#strftime-behavior
# *请注意，这些格式字符串与显示日期的字符串不同
DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
    '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    '%m/%d/%y %H:%M',        # '10/25/06 14:30'
    '%m/%d/%y',              # '10/25/06'
]

# 一周的第一天，用于日历0表示星期日，1表示星期一...
FIRST_DAY_OF_WEEK = 0

# 小数分隔符号
DECIMAL_SEPARATOR = '.'

# 布尔值，设置格式化数字时是否添加千位分隔符
USE_THOUSAND_SEPARATOR = False

# 将它们拆分为THOUSAND_SEPARATOR时将在一起的位数。 0表示没有分组，3表示分成数千...
NUMBER_GROUPING = 0

# 千分隔符号
THOUSAND_SEPARATOR = ','

# 未指定的情况下用于每个模型的表空间。
DEFAULT_TABLESPACE = ''
DEFAULT_INDEX_TABLESPACE = ''

# 默认X-Frame-Options标头值
X_FRAME_OPTIONS = 'SAMEORIGIN'

USE_X_FORWARDED_HOST = False
USE_X_FORWARDED_PORT = False

# Python的dotted路径指向Django内部服务器（runserver）将使用的WSGI应用程序。 如果是“None”，则使用'django.core.wsgi.get_wsgi_application'的返回值，从而保留与先前版本的Django相同的行为。 否则，这应该指向一个实际的WSGI应用程序对象。
WSGI_APPLICATION = None

# 如果您的Django应用程序位于设置标头以指定安全连接的代理后面，并且该代理确保忽略用户提交的具有相同名称的标头（以便人们无法欺骗它），请将此值设置为元组 （header_name，header_value）。 对于带有该标头/值的任何请求，request.is_secure（）将返回True。 警告！ 如果您完全了解自己在做什么，请设置此项。 否则，您可能会面临安全风险。
SECURE_PROXY_SSL_HEADER = None

##############
# MIDDLEWARE #
##############

# 要使用的中间件列表。 秩序很重要; 在请求阶段，这些中间件将按给定的顺序应用，并且在响应阶段，中间件将以相反的顺序应用。
MIDDLEWARE = []

############
# SESSIONS #
############

# 如果使用缓存会话后端，则缓存以存储会话数据。
SESSION_CACHE_ALIAS = 'default'
# Cookie名称。 这可以是你想要的任何东西。
SESSION_COOKIE_NAME = 'sessionid'
# cookie的年龄，以秒为单位（默认值：2周）。
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2
# 类似“example.com”的字符串，或标准域cookie的无。
SESSION_COOKIE_DOMAIN = None
# 会话cookie是否应该是安全的（仅限https：//）。
SESSION_COOKIE_SECURE = False
# 会话cookie的路径。
SESSION_COOKIE_PATH = '/'
# 是否使用非RFC标准的httpOnly标志（IE，FF3 +，其他）
SESSION_COOKIE_HTTPONLY = True
# 是否设置标志限制跨站点请求的cookie泄漏。 这可以是'Lax'，'Strict'或None来禁用该标志。
SESSION_COOKIE_SAMESITE = 'Lax'
# 是否在每个请求上保存会话数据。
SESSION_SAVE_EVERY_REQUEST = False
# Web浏览器关闭时用户的会话cookie是否过期。
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# 用于存储会话数据的模块
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# 如果使用文件会话模块，则存储会话文件的目录。 如果为None，则后端将使用合理的默认值。
SESSION_FILE_PATH = None
# 用于序列化会话数据的类
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

#########
# CACHE #
#########

# 缓存后端使用。
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
CACHE_MIDDLEWARE_KEY_PREFIX = ''
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_ALIAS = 'default'

##################
# AUTHENTICATION #
##################

AUTH_USER_MODEL = 'auth.User'

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

LOGIN_URL = '/accounts/login/'

LOGIN_REDIRECT_URL = '/accounts/profile/'

LOGOUT_REDIRECT_URL = None

# 密码重置链接有效的天数
PASSWORD_RESET_TIMEOUT_DAYS = 3

# 此列表中的第一个哈希是首选算法。 使用不同算法的任何密码将在登录时自动转换
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = []

###########
# SIGNING #
###########

SIGNING_BACKEND = 'django.core.signing.TimestampSigner'

########
# CSRF #
########

# 当CSRF中间件拒绝请求时，可调用的虚线路径用作视图。
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# CSRF cookie的设置。
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_AGE = 60 * 60 * 24 * 7 * 52
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_TRUSTED_ORIGINS = []
CSRF_USE_SESSIONS = False

############
# MESSAGES #
############

# 用作消息后端的类
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# 默认值MESSAGE_LEVEL和MESSAGE_TAGS在django.contrib.messages中定义，以避免在此设置文件中导入。

###########
# LOGGING #
###########

# 用于配置日志记录的callable
LOGGING_CONFIG = 'logging.config.dictConfig'

# 自定义日志配置。
LOGGING = {}

# 默认异常报告者过滤器类，用于没有专门分配给HttpRequest实例的情况。
DEFAULT_EXCEPTION_REPORTER_FILTER = 'django.views.debug.SafeExceptionReporterFilter'

###########
# TESTING #
###########

# 用于运行测试套件的类的名称
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# 在测试数据库创建时不需要序列化的应用程序（只有具有迁移的应用程序才能开始）
TEST_NON_SERIALIZED_APPS = []

############
# FIXTURES #
############

# 要搜索 fixtures 的目录列表
FIXTURE_DIRS = []

###############
# STATICFILES #
###############

# 其他静态文件的位置列表
STATICFILES_DIRS = []

# 构建过程中使用的默认文件存储后端
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 知道如何在不同位置查找静态文件的查找程序类列表。
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
]

##############
# MIGRATIONS #
##############

# 迁移模块按应用标签覆盖应用。
MIGRATION_MODULES = {}

#################
# SYSTEM CHECKS #
#################

# 应该静默的系统检查生成的所有问题的列表。 警告，信息或调试等轻微问题不会生成消息。 消除错误和严重问题等严重问题不会导致隐藏信息，但Django不会阻止您 运行服务器。
SILENCED_SYSTEM_CHECKS = []

#######################
# SECURITY MIDDLEWARE #
#######################
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_HSTS_SECONDS = 0
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_HOST = None
SECURE_SSL_REDIRECT = False
