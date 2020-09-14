from django.db import models


# 实现QQ第三方认证登陆，创建一个模型类的父类
# 这个类最终不要生成数据库的表，而仅仅是用来被继承使用
# 所以我们要在class meta中增加一个关键字abstract = True
# Django 一旦检测到这个类是一个抽象类，它就不会创建表了
class BaseModel(models.Model):
    """为模型类补充字段"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表
