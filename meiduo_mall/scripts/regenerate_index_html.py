#!/usr/bin/env python

"""
功能：手动生成所有SKU的静态detail html文件
使用方法:
    ./regenerate_index_html.py
"""
import sys
import os
import django
from contents.crons import generate_static_index_html


# 从当前文件夹开始，找到导包路径并添加进系统路径
sys.path.insert(0, '../')
sys.path.insert(0, '../meiduo_mall/apps')


if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


# 让django进行初始化设置，数据库连接好
django.setup()


if __name__ == '__main__':
    generate_static_index_html()
