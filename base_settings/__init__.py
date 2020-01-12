import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development base_settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

SECRET_KEY = 'SIMPLE_SECRET_KEY_DO_NOT_USE_IN_PRODUCTION'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_REAL_IP', '127.0.0.1')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Included third-party apps
    'corsheaders',
    'django_fullclean',
    'rest_framework',
    'django_cron',
    'django_filters',
    'django_cleanup',
    # 'reversion',
]

MIDDLEWARE = [
    'django_base.base_utils.middleware.MethodOverrideMiddleware',
    'django_base.base_utils.middleware.ExplicitSessionMiddleware',
    'django_base.base_utils.middleware.CustomExceptionMiddleware',
    'django_base.base_utils.app_error.middleware.AppErrorMiddleware',
    'django_base.base_utils.middleware.GlobalRequestMiddleware',
    # 生产环境建议关闭，使用手动定义的 MEDIA_URL 以及 STATIC_URL
    'django_base.base_utils.middleware.FullMediaUrlMiddleware',
    # 'django_base.base_utils.middleware.DebugMiddleware',
    # 'django_base.base_utils.middleware.CookieCsrfMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django_base.base_utils.middleware.SingleSessionMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': '''
            SET default_storage_engine=MYISAM;
            SET sql_mode='STRICT_TRANS_TABLES';
            ''',
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_general_ci',
        },
    },
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [{
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
}]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

FILE_UPLOAD_PERMISSIONS = 0o644

# =========== REST Framework ==============


REST_FRAMEWORK = {
    # 'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS':
        'django_base.base_utils.pagination.PageNumberPagination',
    # https://stackoverflow.com/a/30875830/2544762
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'django_base.base_utils.authentication.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    # ],
    'DEFAULT_FILTER_BACKENDS': (
        # 'rest_framework_filters.backends.DjangoFilterBackend',
        # 'rest_framework.filters.SearchFilter',
        # 'rest_framework.filters.OrderingFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
        'django_base.base_utils.filters.DeepFilterBackend',
        'django_base.base_utils.filters.OrderingFilter',
        'django_base.base_utils.filters.SearchFilter',
    ),
    # 'DEFAULT_RENDERER_CLASSES': (
    #     # 'rest_framework.renderers.JSONRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer',
    # ),
    'DATE_FORMAT': '%Y-%m-%d',
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'COERCE_DECIMAL_TO_STRING': False,
    # 'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',

    # Parser classes priority-wise for Swagger
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
}

# ============== Models ==============

# TODO: 是否开启假删除
PSEUDO_DELETION = True

# ============== Geo =================

AUTO_GEO_DECODE = False

# 百度地图 API_KEY
BMAP_KEY = 'D373d23acd37b0c4af370a517922e020'
# 高德地图 API_KEY
AMAP_KEY = '426199200d02eb77b7758f87f394a2c9'

# 是否将音频自动转换为 ogg/mp3
NORMALIZE_AUDIO = True
# =========== CORS ===============

# CORS_ORIGIN_ALLOW_ALL = DEBUG
CORS_ORIGIN_REGEX_WHITELIST = r'.*'
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = ['null', '.local', 'localhost', '127.0.0.1']

# ============== Payment ===============

# 如果开启调试，所有实际支付的金额会变成 1 分钱
PAYMENT_DEBUG = True

# =============== SMS Config ===================

SMS_ACCESS_KEY_ID = '----------'
SMS_ACCESS_KEY_SECRET = '----------'

SMS_SEND_INTERVAL = 60  # 短信发送时间间隔限制
SMS_EXPIRE_INTERVAL = 1800
SMS_SIGN_NAME = '短信签名'
SMS_TEMPLATES = dict(
    SIGN_IN='SMS_142655055',
    CHANGE_PASSWORD='SMS_142655052',
    CHANGE_MOBILE_VERIFY='SMS_142655051',
    CHANGE_MOBILE_UPDATE='SMS_142655056',
)
SMS_DEBUG = False  # 不真正发送短信，将验证码直接返回

# =============== JPUSH ==================

JPUSH_APP_KEY = 'a286ac61a069e1bb673c122f'
JPUSH_MASTER_SECRET = 'cf7d0e9a881dc602d23b219d'

# ============== URLS ================

ROOT_URLCONF = 'apps.core.urls'
ENABLE_ADMIN_SITE = True

# ============== CUSTOM SESSION HEADER ==============
CUSTOM_SESSION_HEADER = 'SESSION-ID'

# ============== MethodOverrideMiddleware =================
METHOD_OVERRIDE_ALLOWED_HTTP_METHODS = ['GET', 'HEAD', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'PATCH']
METHOD_OVERRIDE_PARAM_KEY = '_method'
METHOD_OVERRIDE_HTTP_HEADER = 'HTTP_X_HTTP_METHOD_OVERRIDE'

# ============== DJANGO CACHE ===============
# 为了解决 django-cron 的跨进程锁，需要换成 filebased cache
# https://github.com/Tivix/django-cron/issues/41
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

API_DEBUG = False
