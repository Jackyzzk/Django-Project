from celery import Celery

import os


# 为 celery 使用 django 配置文件进行设置
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


celery_app = Celery('meiduo')

# 导入配置文件
celery_app.config_from_object('celery_tasks.config')

# 自动注册celery任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.emails', 'celery_tasks.html'])


# 开启celery的命令
#  celery -A 应用路径（.包路径） worker -l info
#  celery -A celery_tasks.main worker -l info

# 开启 celery 的命令
# celery -A        路径        worker -l info
# celery -A celery_tasks.main worker -l info

# celery -A     <mymodule>    worker -l info -P eventlet
# celery -A celery_tasks.main worker -l info -P eventlet
