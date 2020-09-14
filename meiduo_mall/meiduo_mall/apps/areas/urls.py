from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views


# 创建 router 对象，并注册视图集
router = DefaultRouter()

# register(prefix, viewset, basename)
# prefix 该视图集的路由前缀，即 URL 前缀
# viewset 视图集
# basename 指定视图集生成的视图函数名的前缀
# 这个视图函数的名字是什么呢？django-rest-framework 的默认生成规则是 basename-action
# basename 会自动从视图集 get_queryset 方法返回的结果所关联的 model 获取一个默认值，其值为 model 名小写。
router.register('areas', views.AreasViewSet, basename='area')
# 上式相当于:
# url(r'^areas/(?P<pk>\d+)/$', views.AreasViewSet.as_view({'get': 'retrieve'}))
# url(r'^areas/$', views.AreasViewSet.as_view({'get': 'list'}))
# 默认的 list retrieve 方法已经内置 不需要我们写了？

urlpatterns = [
    # url('', include('router.urls'))
]

urlpatterns += router.urls

# 使用视图集ViewSet，可以将一系列逻辑相关的动作放到一个类中：
# list() 提供一组数据
# retrieve() 提供单个数据
# create() 创建数据
# update() 保存数据
# destroy() 删除数据
# ViewSet视图集类不再实现get()、post()等方法，而是实现动作 action 如 list()、create() 等。
# 视图集只在使用as_view()方法的时候，才会将action动作与具体请求方式对应上。
# urlpatterns = [
#     url(r'^books/$', BookInfoViewSet.as_view({'get':'list'}),
#     url(r'^books/(?P<pk>\d+)/$', BookInfoViewSet.as_view({'get': 'retrieve'})
# ]
# 如果用 GET 方式请求某个 URL 就会调用传入字典的映射关系找到对应的函数进行调用

# ViewSet 继承自 APIView 与 ViewSetMixin，没有提供任何动作 action 方法

# GenericViewSet 继承自 GenericAPIView 与 ViewSetMixin，在 as_view()时传入字典（如{'get':'list'}）映射处理工作

# ModelViewSet继承自GenericViewSet
# 同时包括了ListModelMixin、RetrieveModelMixin、CreateModelMixin、UpdateModelMixin、DestroyModelMixin

# ReadOnlyModelViewSet 继承自 GenericViewSet，同时包括了 ListModelMixin、RetrieveModelMixin

# 在视图集中，我们可以通过 action 对象属性来获取当前请求视图集时的action动作是哪个 print(self.action)

# 路由方式：创建 router 对象，并注册视图集
# 我们实际上不需要自己设计 URL,将资源连接到视图和 url 的约定可以使用 Router 类自动处理


