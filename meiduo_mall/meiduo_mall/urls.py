"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
import xadmin

urlpatterns = [
    # path(r'^admin/', admin.site.urls),  # 有 xadmin 以后就不再用了
    path(r'xadmin/', xadmin.site.urls),
    path('', include('verifications.urls')),
    path('', include('users.urls')),
    path(r'oauth/', include('oauth.urls')),
    path(r'', include('areas.urls')),
    path(r'ckeditor/', include('ckeditor_uploader.urls')),
    path(r'', include('goods.urls')),
    path(r'', include('carts.urls')),
    path(r'', include('orders.urls')),
    path(r'', include('payment.urls')),
]


