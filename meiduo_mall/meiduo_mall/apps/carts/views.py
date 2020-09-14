import base64
import pickle

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer
from goods.models import SKU

# Create your views here.


class CartView(APIView):
    # 需要操作数据库的 queryset, get_queryset, get_object 才需要继承自 GenericAPIView
    # 需要用到序列化器的 serializer_class, get_serializer_class, get_serializer 才需要继承自 GenericAPIView
    # APIView 会在进入具体方法之前做三件事：身份认证，权限检查，限流
    """
    购物车
    """
    def perform_authentication(self, request):
        """重写检查JWT token是否正确"""
        pass

    def post(self, request):
        """保存购物车数据"""
        # 检查前端发送的数据是否正确
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            # 前端携带了错误的 JWT  用户未登录
            user = None

        # 保存购物车数据
        if user is not None and user.is_authenticated:  # 并且不是匿名用户
            # 用户已登录 保存到redis中
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()

            # 购物车数据  hash 键 域 值？
            # 键：cart_< user_id >, 值：{ sku_id1: count1, sku_id2, count2, ... }
            # hincrby key field increment
            # 为哈希表 key 中的域(字段) field 的值加上增量 increment
            pl.hincrby('cart_%s' % user.id, sku_id, count)

            # 勾选
            if selected:
                # sadd key member
                # 将一个或多个 member 元素加入到 key 中
                pl.sadd('cart_selected_%s' % user.id,  sku_id)

            pl.execute()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 用户未登录，保存到cookie中
            # 尝试从cookie中读取购物车数据
            cart_str = request.COOKIES.get('cart')

            if cart_str:
                # 字符串在 Python 内部的表示是 unicode 编码，因此在做编码转换时，通常需要以 unicode 作为中间编码
                # decode 相当于解码，就是相当于一个人脱了衣服（无论穿什么，脱了都一样），解码到 unicode 中间编码
                # encode 编码，相当于一个人可以穿不同的衣服（穿啥由你决定~）

                # 第一步从 cookie 中拿到的是字符串，默认就是中间编码形式存储
                # 字符串 encode 之后得到 byte 类型
                # byte 类型进行 b64 解码，还是得到 byte类型 形如‘x80\x03...’，这个已经是字典的形状了
                # 最后 pickle loads 反序列化，得到字典对象
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            # {
            #     sku_id: {
            #                 "count": xxx, // 数量
            #     "selected": True // 是否勾选
            # },
            # sku_id: {
            #     "count": xxx,
            #     "selected": False
            # },
            # ...
            # }

            # 如果有相同商品，求和
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 第一步，把字典对象 序列化，得到 字典形状的 byte 类型，dumps db 编码
            # 第二步，把字典形式的 byte 类型继续 b64 编码，得到一串 byte 类型
            # 第三步，对 byte 类型解码，得到字符串，也就是 cookie 的最后形式
            cookie_cart = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 返回

            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie('cart', cookie_cart)

            return response

    def get(self, request):
        """查询购物车数据"""
        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            # 前端携带了错误的 JWT  用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 如果用户登录，从redis查询
            redis_conn = get_redis_connection('cart')
            # http://redisdoc.com/
            # hgetall, smembers
            redis_cart = redis_conn.hgetall("cart_%s" % user.id)
            # {
            #     sku_id1: count1,
            #     sku_id2: count2
            # }
            cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

            # 将redis中的数据进行整合，形成一个字典，与cookie中解读的一致，方便数据库查询
            # {
            #   sku_id: {
            #       "count": xxx,
            #       "selected": True // 是否勾选
            # },
            #   sku_id: {
            #       "count": xxx,
            #       "selected": False
            # },
            # ...
            # }
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            # 如果用户未登录，从cookie中查询
            cart_str = request.COOKIES.get('cart')

            if cart_str:

                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        sku_id_list = cart_dict.keys()

        # 数据库查询sku对象
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)
        # 向结果集的商品对象补充 count 和 selected 属性
        for sku in sku_obj_list:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        # 序列化返回
        serializer = CartSKUSerializer(sku_obj_list, many=True)
        return Response(serializer.data)

    def put(self, request):
        # 检查前端发送的数据是否正确
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            # 前端携带了错误的 JWT  用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 如果用户登录，修改redis数据
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()

            # hset key field value 将哈希表 key 中的域 field 的值设为 value
            pl.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                # 勾选增加记录
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                # 未勾选 删除记录 set remove
                pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()

            return Response(serializer.data)

        else:
            # 如果用户未登录，修改cookie数据
            cart_str = request.COOKIES.get('cart')

            if cart_str:

                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }

            cookie_cart = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 返回

            response = Response(serializer.data)
            response.set_cookie('cart', cookie_cart)

            return response

    def delete(self, request):
        """删除"""
        # 检查参数sku_id
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            # 前端携带了错误的 JWT  用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 如果用户登录，修改redis数据
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # hdel 删除哈希表 key 中的一个或多个域，不存在的将会被忽略
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            # cookie
            cart_str = request.COOKIES.get('cart')

            if cart_str:

                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            response = Response(serializer.data)

            if sku_id in cart_dict:
                # 删除字典的键值对
                del cart_dict[sku_id]

                cookie_cart = base64.b64encode(pickle.dumps(cart_dict)).decode()

                response.set_cookie('cart', cookie_cart)

            return response





























