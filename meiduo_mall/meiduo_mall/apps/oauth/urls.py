from django.conf.urls import url

from . import views


# 使用视图函数时，django完成URL解析之后，会直接把request对象以及URL解析器捕获的参数
# (比如re_path中正则表达捕获的位置参数或关键字参数) 丢给视图函数
# 但是在类视图中，这些参数不能直接丢给一个类，所以就有了as_view方法
# as_view()执行完成后，返回一个闭包，这个闭包像视图函数一样接收url解析器传送过来的参数
urlpatterns = [
    url(r'^qq/authorization/$', views.OAuthQQURLView.as_view()),
    url(r'^qq/user/$', views.OAuthQQUserView.as_view()),
]