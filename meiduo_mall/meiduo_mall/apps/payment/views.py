from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from alipay import AliPay
from django.conf import settings

from orders.models import OrderInfo
from .models import Payment
# Create your views here.


class PaymentView(APIView):
    """
    支付宝支付
    /orders/(?P<order_id>\d+)/payment/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        user = request.user
        # 校验订单order_id
        try:
            # 订单的用户和订单的状态相符也是发起支付的前提，不能支付别人的和已经取消的订单
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({'message': "订单信息有误"}, status=status.HTTP_400_BAD_REQUEST)

        # 根据订单的数据，向支付宝发起请求，获取支付链接参数
        with open('keys/app_private_key.pem', 'r') as f1:
            app_private_key_string = f1.read()
        with open('keys/alipay_public_key.pem', 'r') as f2:
            alipay_public_key_string = f2.read()
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        order_string = alipay_client.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )

        # 需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 拼接链接返回前端
        alipay_url = settings.ALIPAY_GATEWAY_URL + '?' + order_string

        return Response({'alipay_url': alipay_url})


class PaymentStatusView(APIView):
    """
    修改支付结果状态
    """
    # put post 区别
    # 在 HTTP 中，PUT 被定义为 idempotent 的方法，POST 则不是
    # idempotent /aɪˈdempətənt/ adj. 幂等的
    # 如果你发布一篇博客，使用 PUT 方法不管在发布时请求多少次最后都只产生一篇博客
    # 而如果使用 POST 方法则可能会产生多篇相同的博客
    def put(self, request):
        # 取出请求的参数
        # django 里面的 GET, 在 drf 是 query_params
        # 返回的是一个 QueryDict，和 python 的字典不同的是，一个键可以包含多个值，一个键可以对应一个列表
        query_dict = request.query_params
        # 将 django 中的 QueryDict 转换 python 的字典，就是调用 dict() 方法
        alipay_data_dict = query_dict.dict()

        sign = alipay_data_dict.pop('sign')

        # 校验请求参数是否是支付宝的
        with open('keys/app_private_key.pem', 'r') as f1:
            app_private_key_string = f1.read()
        with open('keys/alipay_public_key.pem', 'r') as f2:
            alipay_public_key_string = f2.read()
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        # 需要传入去除了签名的 data, signature
        success = alipay_client.verify(alipay_data_dict, sign)

        if success:
            order_id = alipay_data_dict.get('out_trade_no')
            trade_id = alipay_data_dict.get('trade_no')  # 支付宝交易流水号

            # 保存支付数据
            # 修改订单数据
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 查询并更新订单状态 filter update
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).\
                update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
            return Response({'trade_id': trade_id})
        else:
            # 参数据不是支付宝的，是非法请求
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)











