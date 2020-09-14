from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from . import constants
from django.http.response import HttpResponse
from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.libs.yuntongxun.sms import CCP
from . import serializers
from rest_framework.response import Response

from rest_framework.generics import GenericAPIView

from celery_tasks.sms.tasks import send_sms_code

import random

# View, APIView, GenericAPIView
# APIView 是 REST framework 提供的所有视图的基类，继承自 Django 的 View 父类。
# GenericAPIView 继承自APIView，增加了对于列表视图和详情视图可能用到的通用支持方法。

# APIView与View的不同之处在于：
# 传入到视图方法中的是 REST framework 的 Request 对象，而不是 Django 的 HttpRequest 对象；
# 视图方法可以返回 REST framework 的 Response 对象，视图会为响应数据设置（render）符合前端要求的格式；
# 任何 APIException 异常都会被捕获到，并且处理成合适的响应信息；
# 在进行 dispatch() 分发前，会对请求进行身份认证、权限检查、流量控制。
# 支持定义的属性：authentication_classes, permission_classes, throttle_classes

# GenericAPIView支持：
# queryset, serializer_class, pagination_class, filter_backends, lookup_field, lookup_url_kwarg
# 提供的方法：
# get_queryset(self), get_serializer_class(self), get_object(self)
# get_serializer(self, args, *kwargs) 返回序列化器对象
# REST framework会向对象的context属性补充三个数据：request、format、view，这三个数据对象可以在定义序列化器时使用。


class ImageCodeView(APIView):
    def get(self, request, image_code_id):

        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection('verify_codes')

        # redis.setex(key, value, seconds)  set extension?
        # 将值 value 关联到 key ，并将 key 的生存时间设为 seconds (以秒为单位)。
        redis_conn.setex('img_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(GenericAPIView):
    # GenericAPIView 中定义了 serializer_class 属性，并完成了相关方法的调用，在这里重新指向并继承了调用方法
    serializer_class = serializers.CheckImageCodeSerializer

    def get(self, request, mobile):

        # get_serializer 是类方法，能从传入的**kwargs字典中取出所需值
        # mobile 参数被放到了类视图对象的属性 kwargs中了

        # 序列化器与反序列化器的使用
        serializer = self.get_serializer(data=request.query_params)
        # return self._request.GET, self.GET = QueryDict(mutable=True), 用 data 来表示这个查询字典

        # 在提供(创建)序列化器对象的时候，REST framework 会向对象的 context 属性补充传入三个数据
        # request, format, view，这三个可作为新定义的序列化器的属性使用
        # 本次请求的 mobile 参数，可以在 context 属性中拿到，这个属性当作字典使用

        serializer.is_valid(raise_exception=True)

        # 校验通过
        sms_code = '%06d' % random.randint(0, 999999)  # %06d 不够的前端补 0
        redis_conn = get_redis_connection('verify_codes')

        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)  # 1 发送过
        # 使用 redis 的 pipeline 管道一次执行多个命令
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)  # 1 发送过
        pl.execute()  # 可以提升速度

        # 云通讯 改 异步任务
        # ccp = CCP()
        # time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
        # ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_CODE_TEMP_ID)

        # 使用 celery
        send_sms_code.delay(mobile, sms_code)

        return Response({'message': 'ok'})

