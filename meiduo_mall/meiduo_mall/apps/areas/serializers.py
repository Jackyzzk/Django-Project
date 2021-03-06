from rest_framework import serializers

from .models import Area


class AreaSerializer(serializers.ModelSerializer):
    """行政区域信息序列化器"""
    class Meta:
        model = Area  # 从 models.py 中导入的 Area 类
        fields = ('id', 'name')


class SubAreaSerializer(serializers.ModelSerializer):
    """
    子级行政区划信息
    """
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')