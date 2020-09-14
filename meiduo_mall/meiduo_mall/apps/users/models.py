from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings

from meiduo_mall.utils.models import BaseModel
from . import constants

# Create your models here.


class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # openid = 第三方登陆，如果我们在这里创建一个适用于QQ的登陆，如果还需要其他的微博登陆等等
    # 就会需要创建很多个字段，很不方便，需要额外创建一张表 oauth/models.py

    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # 在 models.py 中添加字段以后，需要重新数据库迁移
    # python manage.py makemigration
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_send_sms_code_token(self):
        """
        生成发送短信验证码的access_token
        :return: access_token
        """
        # 创建itsdangerous模型的转换工具
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.SEND_SMS_CODE_TOKEN_EXIPIRES)
        data = {
            'mobile': self.mobile
        }
        token = serializer.dumps(data)
        # json.dumps(): 将一个Python数据类型进行json格式的编码解析(dict转成str)
        # serializer.dumps() 将python对象序列化并返回一个bytes对象
        # dumps 后返回 bytes类型，decode 变成字符串
        # serializer.loads(): 将bytes反序列化并返回一个对象(bytes转成之前的数据类型)?

        return token.decode()

    @staticmethod
    def check_send_sms_code_token(token):
        """
        检验access token
        :param token: access token
        :return: mobile  None
        """
        # 创建 itsdangerous 模型的转换工具
        # itsdangerous 提供了一个URL安全序列化工具，生成临时身份令牌
        serialier = TJWSSerializer(settings.SECRET_KEY, constants.SEND_SMS_CODE_TOKEN_EXIPIRES)
        try:
            # json.loads:把json化的字符串转换成对应的python对象
            # json.dumps：把python对象(诸如dict/list/tuple/string等数据结构)转换为字符串
            # loads 解码 dumps 编码
            data = serialier.loads(token)
        except BadData:
            return None
        else:
            mobile = data.get('mobile')
            return mobile

    def generate_set_password_token(self):
        """
        生成修改密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        data = {'user_id': self.id}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_set_password_token(token, user_id):
        """
        检验设置密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            if user_id != str(data.get('user_id')):
                return False
            else:
                return True

    def generate_email_verify_url(self):
        """生成邮箱验证链接"""
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.EMAIL_VERIFY_TOKEN_EXPIRES)
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data)
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token.decode()
        return verify_url

    @staticmethod
    def check_email_verify_token(token):
        """检验token"""
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.EMAIL_VERIFY_TOKEN_EXPIRES)

        # 检验就是对 token 的解码 loads？
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            email = data.get('email')
            user_id = data.get("user_id")
            # user = User.objects.get(id=user_id, email=email)
            # user.email_active = True
            # user.save()
            # 一句话直接查询出来 并更新 等同于上面三句话的效果
            User.objects.filter(id=user_id, email=email).update(email_active=True)
            return True


class Address(BaseModel):
    """
    用户地址
    """
    # 关系型数据库中的一条记录中有若干个属性，若其中某一个属性组(注意是组)能唯一标识一条记录，该属性组就可以成为一个主键
    # 表的外键是另一表的主键，用于与另一张表的关联，是能确定另一张表记录的字段，用于保持数据的一致性。

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    # on_delete=models.CASCADE 级联删除，也就是当删除主表的数据的时候，从表中的数据也随着一起删除。
    # related_name 定义了以后，由 user.address_set.all() 变成 user.addresses.all()
    
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')

    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')

    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']


# 查询买主买了哪些水果，首先要根据条件找到买主信息，然后根据买主信息找到买主所购买的水果
# class Buyer(models.Model):
#     ....
# class Fruit(models.Model):
#     buyer = models.ForeignKey(Buyer, related_name='buyer_fruit')
#     ....

# buyer = Buyer.objects.filter(age = 100).first()
# buyer 对象默认带了一个外键的属性，以子表的名称小写加上_set()来表示，即 fruit_set
# fruits = buyer.fruit_set.all()
# 定义了 related_name='buyer_fruit' 之后，buyer_fruit 取代了默认的 fruit_set
# fruits = buyer.buyer_fruit.all()








