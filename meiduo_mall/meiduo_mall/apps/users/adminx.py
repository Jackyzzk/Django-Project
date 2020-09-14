import xadmin
from .models import User
from xadmin.plugins import auth


class UserAdmin(auth.UserAdmin):
    list_display = ['id', 'username', 'mobile', 'email', 'date_joined']
    readonly_fields = ['last_login', 'date_joined']
    search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile')
    # 给用户角色权限和组添加左右两边调整样式 m to m transfer
    style_fields = {'user_permissions': 'm2m_transfer', 'groups': 'm2m_transfer'}

    def get_model_form(self, **kwargs):
        # org_obj 原始数据对象（User）
        if self.org_obj is None:
            # 添加用户表单
            self.fields = ['username', 'mobile', 'is_staff']
        # 添加手机，职员状态字段，剩下全部继承父类
        return super().get_model_form(**kwargs)


xadmin.site.unregister(User)  # 要先添加反注册
xadmin.site.register(User, UserAdmin)