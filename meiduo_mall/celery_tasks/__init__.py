# Celery 使用步骤

# 1、创建 Celery_app：
# celery_app = Celery('xxx')

# 2、导入配置文件
# celery_app.config_from_object('celery_tasks.config')

# 3、在 Celery_tasks 目录下，创建具体功能文件夹(包)以及 tasks.py
# @celery_app.task(name='xxx')
# def xxx(*args):

# 4、在 main 中注册 Celery 任务
# 自动注册celery任务
# celery_app.autodiscover_tasks(['xxx1', 'xxx2'])

# 5、在主程序中调用
# xxx.delay()
