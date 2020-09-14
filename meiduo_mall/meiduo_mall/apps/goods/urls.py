from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUListView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),
]

# 视图集 与 注册路由
router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, basename='skus-search')

urlpatterns += router.urls
