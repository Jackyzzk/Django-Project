from haystack import indexes
from .models import SKU


# 通过创建索引类来指明，让搜索引擎对哪些字段建立索引
class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    # text 复合字段
    text = indexes.CharField(document=True, use_template=True)  # template/search/indexes/goods/sku_text.txt
    # model_attr 指定该字段从模型类的哪里映射过来的，但是还没有指定通过哪个数据库的表
    # 需要定义 get_model 指定哪个模型类
    id = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr='name')
    price = indexes.CharField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)  # 下架商品不要创建索引让用户搜索出来


# python manage.py rebuild_index
