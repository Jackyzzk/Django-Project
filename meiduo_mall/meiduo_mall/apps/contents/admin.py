from django.contrib import admin

from . import models

# 进入 admin 站点注册数据？

admin.site.register(models.ContentCategory)
admin.site.register(models.Content)