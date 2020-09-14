from django.conf import settings
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
import logging
import json

from .exceptions import QQAPIException

logger = logging.getLogger('django')


class OAuthQQ(object):
    """
    用户QQ登陆的工具类，
    提供了QQ登录可能使用的方法
    """
    # 作为对象属性而不是类属性，所以需要初始化方法
    def __init__(self, app_id=None, app_key=None, redirect_url=None, state=None):
        self.app_id = app_id or settings.QQ_APP_ID
        self.app_key = app_key or settings.QQ_APP_KEY
        self.redirect_url = redirect_url or settings.QQ_REDIRECT_URL
        self.state = state or settings.QQ_STATE

    def generate_qq_login_url(self):
        """
        拼接用户QQ登录的链接地址
        :return: 链接地址
        """
        url = 'https://graph.qq.com/oauth2.0/authorize?'
        data = {
            'response_type': 'code',
            'client_id': self.app_id,
            'redirect_uri': self.redirect_url,  # uri
            'state': self.state,
            'scope': 'get_user_info'  # 获取用户的qq的openid
        }
        # 查询字符串可利用 urlencode 得到
        query_string = urlencode(data)
        # query_string 会等于 ‘response_type=code&client_id=xxx&redirect_uri=xxx&...’
        url += query_string
        print(url)

        return url

    def get_access_token(self, code):
        """
        获取qq的access_token
        :param code: 调用的凭据
        :return: access_token
        """
        url = 'https://graph.qq.com/oauth2.0/token?'
        req_data = {
            'grant_type': 'authorization_code',
            'client_id': self.app_id,
            'client_secret': self.app_key,
            'code': code,
            'redirect_uri': self.redirect_url
        }
        # urlencode 将查询字典转换为 url 的查询字符串
        url += urlencode(req_data)

        try:
            # 我们的后端服务器向其他的服务器(QQ)发送url请求，使用 urlopen 这个函数，没有 data 时候为 GET
            # 返回的 response 响应对象，需要通过 read() 读取，且读出为 bytes 类型
            response = urlopen(url)
            # 读取QQ返回的响应体数据
            # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE1
            response = response.read().decode()

            # parse_qs 可以把返回的查询字符串转换为字典，parse 分析，qs querystring
            resp_dict = parse_qs(response)

            access_token = resp_dict.get("access_token")[0]
            # 后面[0]的原因是，parse_qs 的源码中，parsed_result[name].append(value)
            # 它的值是作为一个列表来保存的(append)
        except Exception as e:
            logger.error(e)
            raise QQAPIException('获取access_token异常')

        return access_token

    def get_openid(self, access_token):
        """
        获取用户的openid
        :param access_token: qq提供的access_token
        :return: open_id
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        try:
            response = urlopen(url)
            response_data = response.read().decode()
            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            # 返回的既不是一个 json 也不是一个标准的查询字符串，它的前面还有 callback 等字符
            # 编码：把一个Python对象编码转换成Json字符串   json.dumps()
            # 解码：把Json格式字符串解码转换成Python对象   json.loads()
            data = json.loads(response_data[10:-4])
        except Exception:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIException('获取openid异常')

        openid = data.get('openid', None)
        return openid














