"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# sys.path保存了python解释器的导包路径
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
sys.path.insert(0, os.path.join(BASE_DIR, 'extra_apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY 是在 startproject 时候生成的，调用的是如下生成代码
# from django.core.management import utils
# utils.get_random_secret_key()
# A secret key for a particular Django installation.
# This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
# 制作 hash等
SECRET_KEY = '&+q5st03g9)81))xki7gyznnu_3f$15ovxwq@i2h0(cinq3v$4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['api.meiduo.site', '127.0.0.1']


# Application definition
# contrib /'kɔn,trɪb/  n. 普通发布版
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',

    # 配合后面的 session_engine 设置了 session 的存放位置
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',

    # The World Wide Web Consortium (W3C) /kənˈsɔːrtiəm/  n. 财团；联合；合伙
    # CORS 是一个w3c标准,全称是"跨域资源共享"(Cross-origin resource sharing)
    # 浏览器默认的安全限制为同源策略，即 JavaScript 或 Cookie 只能访问同源（相同协议，相同域名，相同端口）下的内容
    'corsheaders',
    'ckeditor',  # 富文本编辑器
    'ckeditor_uploader',  # 富文本编辑器上传图片模块
    # 'django_crontab',  # 定时任务
    'haystack',  # 对接搜索引擎 elasticsearch 的中间件
    # Haystack 是 Django 框架的搜索扩展模块。Haystack 提供统一的 API 允许你使用不同的搜索后端
    'xadmin',
    'crispy_forms',
    'reversion',  # 版本追踪？
    'users.apps.UsersConfig',
    'verifications.apps.VerificationsConfig',
    'oauth.apps.OauthConfig',
    'areas.apps.AreasConfig',
    'goods.apps.GoodsConfig',
    'contents.apps.ContentsConfig',
    'carts.apps.CartsConfig',
    'orders.apps.OrdersConfig',
    'payment.apps.PaymentConfig',
]
# install_apps 有什么用？
# Django 使用 INSTALLED_APPS 作为查找模型,管理命令,测试和其他实用程序的所有位置的列表.
# 购物车没有数据库和模板

# 所有不直接给客户直接提供业务价值的软件，都是中间件。举例说明，nginx和 WebSphere App Server、MySQL都是中间件
# 处于基础设施层的软件与业务系统软件中间这一层的一些软件或者库、框架，我们叫中间件，不一定是独立的程序。
# 计算机领域的任何问题都可以通过一个中间层来解决。
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Web 服务器网关接口（Python Web Server Gateway Interface，缩写为 WSGI）
# 指定了 web 服务器和 Python web 应用或 web 框架之间的标准接口，以提高 web 应用在一系列 web 服务器间的移植性。
# 请求时 Web 服务器需要和 web 应用程序进行通信，web 服务器有很多种，Python web 应用开发框架也对应多种，所以 WSGI 应运而生，定义了一套通信标准。

# WSGI 规定，Web 程序必须有一个可调用对象，且该可调用对象接收两个参数，返回一个可迭代对象：
# environ：字典，包含请求的所有信息
# start_response：在可调用对象中调用的函数，用来发起响应，参数包括状态码，headers等
WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'root',
        'NAME': 'pycharm'
    },
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': 3306,  # 8306
        'USER': 'root',
        'PASSWORD': 'root',
        'NAME': 'pycharm'
    },
}

# 数据库路由，自定义数据库读写规则
DATABASE_ROUTERS = ['meiduo_mall.utils.db_routers.MasterSlaveDBRouter']

# 把缓存设置成 redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_codes": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "cart": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
# 设置session的保存位置，有三种方法：
# 保存在关系型数据库(db)
# 保存在缓存数据库(cache) 或者 关系+缓存数据库(cache_db)
# 保存在文件系统中(file)
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# 使用的缓存别名，此处别名依赖缓存的设置
SESSION_CACHE_ALIAS = "session"

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {  # 检查密码和用户某些属性的相似性
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {  # 检查密码的最小长度(默认8)
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {  # 检查密码是否出现在常用密码表中
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {  # 检查密码是否全为数字
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'


# 日志处理
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/meiduo.log"),
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
        },
    }
}


# REST配置
REST_FRAMEWORK = {
    # 异常处理
    'EXCEPTION_HANDLER': 'meiduo_mall.utils.exceptions.exception_handler',

    # 认证机制后端
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),

    # 分页
    'DEFAULT_PAGINATION_CLASS':  'meiduo_mall.utils.paginations.StandardPageNumPagination',
}

# JSONWebToken Authentication
JWT_AUTH = {
    # JWT 的有效期，payload 有效载荷
    # JWT_RESPONSE_PAYLOAD_HANDLER 自定义 jwt 认证成功返回数据，补充字段
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler',
}

# Django认证系统使用的模型类
# model 会自动定位到该目录下的 models.py 文件中去寻找 User 类
AUTH_USER_MODEL = 'users.User'

# Django的认证后端方法
AUTHENTICATION_BACKENDS = [
    # 自定义的后端认证方法，可以增加手机号和用户名共同作为登陆账号
    'users.utils.UsernameMobileAuthBackend',
]

CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080',
    'http://127.0.0.1:8000',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://api.meiduo.site:8000',
)

CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie


# 用于QQ登录的配置信息
QQ_APP_ID = '101474184'
QQ_APP_KEY = 'c6ce949e04e12ecc909ae6a8b09b637c'
QQ_REDIRECT_URL = 'http://www.meiduo.site:8080/oauth_callback.html'

QQ_STATE = '/'


# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = '2395758530@qq.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_FROM = 'Jackyzzk<2395758530@qq.com>'


# DRF扩展
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    # 缓存存储
    'DEFAULT_USE_CACHE': 'default',
}


# FastDFS
# BASE DIR 拼接路径
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')
FDFS_BASE_URL = 'http://127.0.0.1:8888/'

# 重写django文件存储
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.storage.FastDFSStorage'

# 富文本编辑器ckeditor配置
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具条功能全部展示
        'height': 300,  # 编辑器高度
        # 'width': 300,  # 编辑器宽
    },
}
CKEDITOR_UPLOAD_PATH = ''  # 上传图片保存路径，使用了FastDFS，所以此处设为''

# 生成的静态 html 文件保存目录
GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc')

# 定时任务
# CRONJOBS = [
#     # 每5分钟执行一次生成主页静态文件
#     # Linux 中 >> 表示追加
#     ('*/5 * * * *', 'contents.crons.generate_static_index_html',
#      '>> /Users/delron/Desktop/meiduo/meiduo_mall/logs/crontab.log')
# ]

# 解决crontab中文问题
# CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'


# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',  # 此处为elasticsearch运行的服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo',  # 指定elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
# 索引结构需要在django运行起来之前生成，新的数据到来，指定一个新的处理器实时产生新的索引
# 索引结构是在什么时候生成的？一个是在项目运行之前手动生成，第二个通过处理器检测新数据实时的创建新的索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'


# 支付宝
ALIPAY_APPID = 2021000116680255
ALIPAY_DEBUG = True  # 沙箱环境 True
ALIPAY_GATEWAY_URL = 'https://openapi.alipaydev.com/gateway.do'

# 收集静态文件的目录
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc/static')
# python manage.py collectstatic

# 配置 Nginx
# 修改 Nginx/conf/nginx.conf
# server -> location -> root

# 启动 Nginx
# start Nginx
