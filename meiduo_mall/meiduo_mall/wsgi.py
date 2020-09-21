"""
WSGI config for meiduo_mall project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.prod")

application = get_wsgi_application()


# WSGI，全称Web Server Gateway Interface，或者 Python Web Server Gateway Interface，
# 是为Python语言定义的Web服务器和Web应用程序或框架之间的一种简单而通用的接口，基于现存的CGI标准而设计的。
# WSGI其实就是一个网关(Gateway)，其作用就是在协议之间进行转换。

# uWSGI 是一个 Web 服务器，它实现了 WSGI 协议、uwsgi、http等协议。注意 uwsgi 是一种通信协议，
# 而 uWSGI 是实现 uwsgi 协议和 WSGI 协议的 Web 服务器。uWSGI 具有超快的性能、低内存占用和多 app 管理等优点。

# runserver 方法是调试 Django 时经常用到的运行方式，它使用 Django 自带的 WSGI Server 运行，主要在测试和开发中使用
# uWSGI+Nginx 的方法是现在最常见的在生产环境中运行 Django 的方法