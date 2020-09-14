from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from rest_framework.generics import CreateAPIView

from goods.models import SKU


# Create your views here.
from .serializers import OrderSettlementSerializer, SaveOrderSerializer


class OrderSettlementView(APIView):
    """
    订单结算
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        获取
        """
        user = request.user

        # 从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
            sku.selected = True

        # 运费，decimal 是精确的小数保存，float 是浮点计算前保存？
        freight = Decimal('10.00')

        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})
        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    """保存订单"""
    # 如果我们自己写 post 方法
    # 会经过 校验参数，保存到数据库，返回 order_id
    # 正好跟 drf 给我们的创建逻辑一样 CreateAPIView
    permission_classes = [IsAuthenticated]  # 必须是登陆之后
    serializer_class = SaveOrderSerializer  # 校验和保存都放到序列化器里面做
