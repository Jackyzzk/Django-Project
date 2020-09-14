from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework.filters import OrderingFilter
from drf_haystack.viewsets import HaystackViewSet

from .serializers import SKUSerializer, SKUIndexSerializer
from .models import SKU
from . import constants


# 加缓存
# 因为 ListAPIView 继承了 ListModelMixin 已经把 list 方法拿过来了
class HotSKUListView(ListCacheResponseMixin, ListAPIView):
    # ListAPIView 父类调用了self.filter_queryset()，self.get_queryset()，
    # self.paginate_queryset()，self.get_serializer()，self.get_paginated_response()
    # 最终返回了列表数据(多个)
    """返回热销数据
    /categories/(?P<category_id>\d+)/hotskus/
    """
    # queryset = SKU.objects.all()  放到这能不能行呢？
    # 不行吧，它会把所有的都返回，而我们需要根据 category_id 来查询
    # 我们要调整 queryset 有没有办法？—— 重写 get_queryset 方法

    serializer_class = SKUSerializer
    pagination_class = None  # 定义了全局的分页，但是热销不需要

    def get_queryset(self):
        # category_id 从哪来呢？从路径中来，需要从路径中获取
        # 这里的 self 在类视图中可以直接操作 self.kwargs
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:constants.HOT_SKUS_COUNT_LIMIT]


class SKUListView(ListAPIView):
    """
    商品列表数据
    /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
    """
    # 并不是把所有的返回 所以不用 SKU.object.all()，所以要重写 get_queryset
    serializer_class = SKUSerializer

    # 通过定义过滤后端，来实现排序行为，添加过滤器
    filter_backends = [OrderingFilter]
    # 给过滤器添加过滤字段，从模型类当中来
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer
