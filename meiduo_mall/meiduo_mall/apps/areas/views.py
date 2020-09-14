from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
# pip3 install drf-extensions
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area
from . import serializers


# 视图集，不用手写映射关系？
# 省市区  经常访问 放缓存  减少数据库的读取
class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    # 进来的时候先看缓存有没有数据
    """
    list: 返回所有省份的信息
    retrieve: 返回特定省或市的下属行政规划区域
    """
    # 关闭分页处理
    pagination_class = None

    # queryset = Area.objects.all()
    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)  # 所有的顶级
        else:
            return Area.objects.all()

    # GenericAPI 内部调用序列化器的方法，我们可以重写这个方法来实现根据不同的需求来调用不同的序列化器
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AreaSerializer
        else:
            return serializers.SubAreaSerializer

# CreateModelMixin: 定义了创建一个序列对象的方法
# create(self, request, *args, **kwargs)，保存方法perform_create(self, * * * serializer)
# 成功获取请求头的方法：get_success_headers(self, data)

# ListModelMixin： 定义了一个获取查询集的方法， many=True：list(self, request, *args, **kwargs)

# RetrieveModelMixin: 定义了一个检索方法，retrieve(self, request, *args, **kwargs)

# UpdateModelMixin： 更新一个模型实例，update(self, request, *args, **kwargs)

# DestroyModelMixin： 删除一个模型实例，方法destroy(self, request, *args, **kwargs)
