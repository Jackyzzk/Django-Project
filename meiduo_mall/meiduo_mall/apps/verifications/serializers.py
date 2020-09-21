from rest_framework import serializers
from django_redis import get_redis_connection
from redis.exceptions import RedisError
import logging


logger = logging.getLogger('django')

# 序列化器：
# 实质: 定义了一个叫做 xx序列化器 的 <类>，
# 作用:
#      1. 实现 <json> 和 <对象> 的相互转化
#      2. 实现对 前端数据 的校验功能
# 序列化       读取（read_only） 数据库         obj(数据库)   ->       json
# 反序列化     写入 (write_only) 数据库            json      ->     obj(数据库)


class CheckImageCodeSerialzier(serializers.Serializer):
    """
    图片验证码校验序列化器
    GenericAPIView  ->  get_serializer()  context
    """
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(min_length=4, max_length=4)

    # 调用 serializer.is_valid 的时候是怎么关联到 validate 函数的？
    # is_valid()方法，做了两件事，一个把验证过的数据赋值给 validated_data 属性，一个返回布尔值判断数据是否验证通过
    # 调用 Serializer 类中 run_validation() 方法
    # 1、调用Serializer类中to_internal_value()方法，目的是将原始数据转换成Django中的字典类型
    # 2、调用Serializer类中run_validators()方法，验证每个字段值
    # 3、调用Serializer类中validate()方法, 目的是返回经过校验的数据，没有做任何处理，可以自定义

    def validate(self, attrs):
        """校验图片验证码是否正确"""
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 查询redis数据库，获取真实的验证码
        redis_conn = get_redis_connection('verify_codes')
        real_image_code = redis_conn.get('img_%s' % image_code_id)

        if real_image_code is None:
            # 过期或者不存在
            raise serializers.ValidationError('无效的图片验证码')

        # 删除redis中的图片验证码，防止用户对同一个进行多次请求验证
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)

        # 对比
        real_image_code = real_image_code.decode()  # 解码，decode the bytes，bytes -> string
        if real_image_code.lower() != text.lower():  # 小写校验
            raise serializers.ValidationError('图片验证码错误')

        # redis中发送短信验证码的标志 send_flag_<mobile>  : 1, 由redis维护60s的有效期
        mobile = self.context['view'].kwargs.get('mobile')
        if mobile:
            send_flag = redis_conn.get('send_flag_%s' % mobile)
            if send_flag:
                raise serializers.ValidationError('发送短信次数过于频繁')

        return attrs



