from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import mixins
import re
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from . import serializers
from .models import User
from verifications.serializers import CheckImageCodeSerialzier
from .utils import get_user_by_account
from . import constants
from goods.models import SKU
from goods.serializers import SKUSerializer
from carts.utils import merge_cart_cookie_to_redis

# Create your views here.


class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserView(CreateAPIView):
    """
    用户注册
    """
    serializer_class = serializers.CreateUserSerializer


class SMSCodeTokenView(GenericAPIView):
    # GenericAPIView的两个属性：
    # queryset: 指明视图需要的数据，针对从数据库中获取数据。如果是从前端获取数据就就从 request 中获取。
    # serializer_class: 指明视图使用哪个序列化器
    # 如果你用了上面的属性，就必须需要使用对应的 get_queryset 和 get_serializer 进行操作
    # get_queryset功能：从类属性 queryset 中获取 model 的 queryset 数据
    # get_serializer功能：从类属性 serializer_class 中获得 serializer 的序列化类，主要是给 Mixin 扩展类使用
    # CreateModelMixin（增加）,DestroyModelMixin（删除）,ListModelMixin（查询,查queryset）
    # RetrieveModelMixin（查询，查对象，针对于存在"pk"）,UpdateModelMixin（修改）

    """获取发送短信验证码的凭据"""
    serializer_class = CheckImageCodeSerialzier

    def get(self, request, account):
        # 校验图片验证码

        # 定义了 serializer_class 属性的指向后，便可以提供 get_serializer 方法
        # get_serializer(self, args, *kwargs)
        # 返回序列化器对象，主要用来提供给Mixin扩展类使用
        # 该方法在提供序列化器对象的时候，会向序列化器对象的context属性补充三个数据：
        # request、format、view，这三个数据对象可以在定义序列化器时使用。
        serializer = self.get_serializer(data=request.query_params)
        # request,当前视图的请求对象;view,当前请求的类视图对象;format,当前请求期望返回的数据格式
        # 判断用户是否在60s内使用同一个手机号码获取短信
        # mobile为手机号。通过context来获取当前类视图对象，通过kwargs来获取mobile。
        # mobile = self.context['view'].kwargs['mobile']
        # send_flag = redis_conn.get('send_flag_%s' % mobile)
        # if send_flag:
        #   raise serializers.ValidationError('频繁发送短信')
        serializer.is_valid(raise_exception=True)

        # 根据account查询User对象
        user = get_user_by_account(account)
        if user is None:
            return Response({"message": '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 根据User对象的手机号生成access_token
        access_token = user.generate_send_sms_code_token()

        # 正则表达式实现隐藏手机号部分片段
        mobile = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', user.mobile)

        return Response({
            'mobile': mobile,
            'access_token': access_token
        })


class PasswordTokenView(GenericAPIView):
    """
    用户帐号设置密码的token
    """
    serializer_class = serializers.CheckSMSCodeSerializer

    def get(self, request, account):
        """
        根据用户帐号获取修改密码的token
        """
        # 校验短信验证码
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        # 生成修改用户密码的access token
        access_token = user.generate_set_password_token()

        return Response({'user_id': user.id, 'access_token': access_token})


class PasswordView(mixins.UpdateModelMixin, GenericAPIView):
    """
    用户密码
    """
    queryset = User.objects.all()
    serializer_class = serializers.ResetPasswordSerializer

    # 利用 updatemodelmixin 来更新密码
    # 把post方式映射扩展至update？继承自两个类？
    def post(self, request, pk):
        return self.update(request, pk)


class UserDetailView(RetrieveAPIView):
    """用户详情信息
    /users/<pk>/

    /user/
    """
    # def get(self, request):
    #     request.user
    #
    # def post(self, request):

    serializer_class = serializers.UserDetailSerializer
    # 权限类配置方法
    # 补充通过认证才能访问接口的权限
    permission_classes = [IsAuthenticated]

    # 重写 get_object 方法
    def get_object(self):
        """
        返回请求的用户对象
        :return: user
        """
        # drf 框架中 request 有 query_params，data 属性之外，还有一个 user 属性
        # request 还可直接作为类视图对象存在
        # request 对象的 user 属性是通过认证检验之后的请求用户对象
        # 类视图对象除了 request 之外还有 kwargs 属性
        # 它在我们的序列化器中用过 account = self.context['view'].kwargs['account']
        return self.request.user


class EmailView(UpdateAPIView):

    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 重写 get_object 方法，instance = self.get_object()
        return self.request.user

    # def get_serializer(self, *args, **kwargs):
    #   # serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     return EmailSerializer(self.request.user, data=self.request.data)


class EmailVerifyView(APIView):
    """邮箱验证"""
    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 校验  保存
        result = User.check_email_verify_token(token)

        if result:
            return Response({"message": "OK"})
        else:
            return Response({"非法的token"}, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = serializers.UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = serializers.UserAddressSerializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserHistoryView(mixins.CreateModelMixin, GenericAPIView):
    # 查询时不能用 ListModelMixin 的原因，数据来源不是数据库
    """用户历史记录"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AddUserHistorySerializer

    def post(self, request):
        """保存"""
        return self.create(request)

    def get(self, request):
        user_id = request.user.id
        # 查询redis数据库
        redis_conn = get_redis_connection('history')
        # lrange 从 redis 取出数据
        sku_id_list = redis_conn.lrange('history_%s' % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT)

        # 根据redis返回的sku id 查询数据
        # SKU.objects.filter(id__in=sku_id_list)  可以用 in 但是顺序会被打乱
        sku_list = []
        for sku_id in sku_id_list:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)

        # 使用序列化器序列化，用了热销商品的序列化器
        serializer = SKUSerializer(sku_list, many=True)
        return Response(serializer.data)


class UserAuthorizationView(ObtainJSONWebToken):
    # JWT Token 登陆逻辑重写，实现登陆时合并购物车

    def post(self, request):
        # 调用父类的 post 方法，实现继承并追加新功能，省去复制一大段过来，父类最后返回的是 response 对象
        response = super().post(request)

        # 如果用户登录成功，进行购物车数据合并
        # 构建序列化器的时候 要传数据？
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 表示用户登录成功
            user = serializer.validated_data.get("user")
            # 调用我们自己的方法，合并购物车
            response = merge_cart_cookie_to_redis(request, response, user)

        return response














































