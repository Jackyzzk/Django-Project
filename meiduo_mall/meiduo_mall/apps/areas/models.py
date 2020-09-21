from django.db import models


class Area(models.Model):
    # Model 继承自 ModelBase
    """
    行政区划
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs',
                               null=True, blank=True, verbose_name='上级行政区划')
    # 主表：存在主键(primary key)用于与其它表相关联，并且作为在主表中的唯一性标识。
    # 从表：以主表的主键（primary key）值为外键 (Foreign Key)的表，可以通过外键与主表进行关联查询。
    # django 默认每个主表的对象都有一个是外键的属性，可以通过它来查询到所有属于主表的子表的信息。
    # related_name 这个参数的意义就是，不再采用默认的类名 + _set 去获取数据，而是我自己指定
    # 默认是通过 模型类名 + _set 来进行查询，假如 area1 是一个实例对象
    # area1.subs 与 area_set

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name

# python manage.py makemigrations
# python manege.py migrate

# 所有的省市区数据 放在了 scripts\areas.sql 中
# 可以导入数据库即可
# mysql -h 127.0.0.1 -u root -p root pycharm < ./areas.sql
# 把上述代码写成脚本文件 .sh
# 以后只要执行 ./import_areas_data_to_db.sh
# #! 声明运行解释器
# chmod +x ./import_areas_data_to_db.sh 加上可执行权限

# 同理 可以让一个 xxx.py 具备可执行能力的步骤：
# xxx.py 文件的头部加上 #!/usr/bin/env python
# chmod +x xxx.py
# 运行 ./xxx.py 即可


# area1.subs 通过这个属性，可以获取相关的多数集合的数据（下属的下级规划区域）
# 默认是通过 类型_set来进行查询（area_set)， 通过指明related_name参数后，直接通过参数的数据来查询
