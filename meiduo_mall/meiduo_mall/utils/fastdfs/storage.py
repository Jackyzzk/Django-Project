from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client
from django.conf import settings


# 存储类必须是 deconstructible，以便在迁移中的字段上使用它时可以序列化。
# 只要你的字段有自己的参数可以自动序列化，你可以使用django.utils.deconstruct.deconstructible类装饰器
@deconstructible
class FastDFSStorage(Storage):
    """自定义的文件存储系统"""
    def __init__(self, client_conf=None, base_url=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_BASE_URL
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        """
        保存文件
        :param name:  前端传递的文件名
        :param context: 文件数据
        :return: 存储到数据库中的文件名
        """
        # 保存到FastDFS
        client = Fdfs_client(self.client_conf)

        # 传过来的 content 是具体的文件对象，需要调用 read 方法
        ret = client.upload_by_buffer(content.read())

        if ret.get("Status") != "Upload successed.":
            raise Exception("upload file failed")

        file_name = ret.get("Remote file_id")

        return file_name

    def exists(self, name):
        return False

    def url(self, name):
        """
        在获取 ImageFiled 字段数据的 url 属性时，django 会调用 url 方法获取文件的完整路径
        :param name: 从数据库中读出的字段值 也就是之前保存的file_name  Remote file_id
        :return:
        """
        # name 就是上面 _save 存入数据库的数据
        return self.base_url + name

