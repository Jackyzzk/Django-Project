import base64
import pickle

from django_redis import get_redis_connection


# 读取 cookie 需要 request 对象，从 cookie 中清除数据，需要操作 response 对象的 del 方法
def merge_cart_cookie_to_redis(request, response, user):
    """
    合并购物车，把 cookie 的数据覆盖保存到 redis 中
    :return: 
    """
    # 从cookie中取出购物车数据
    cart_str = request.COOKIES.get('cart')
    # 如果 cookie 明明有数据但是却获取不到，是由于跨域访问，需要在前端 js 文件中携带上 withCredentials: True

    if not cart_str:
        return response  # 这里不能返回 None

    cookie_cart = pickle.loads(base64.b64decode(cart_str.encode()))

    # {
    #     sku_id: {
    #                 "count": xxx, // 数量
    #             "selected": True // 是否勾选
        # },
        # sku_id: {
        #     "count": xxx,
        #     "selected": False
        # },
        # ...
    # }

    # 从redis中取出购物车数据
    redis_conn = get_redis_connection('cart')
    cart_redis = redis_conn.hgetall('cart_%s' % user.id)

    cart = {}
    for sku_id, count in cart_redis.items():
        # 把 redis 取出的字典的键值对数据类型 转换为 int，之前都是 byte
        cart[int(sku_id)] = int(count)

    # {
    #     sku_id1: count1,
    #     sku_id2: count2
    # }

    selected_sku_id_list = []
    for sku_id, selected_count_dict in cookie_cart.items():  # 第二项是一个小字典
        # 直接覆盖，思想是最后一次操作是未登录
        cart[sku_id] = selected_count_dict['count']

        # 处理勾选状态，
        if selected_count_dict['selected']:
            selected_sku_id_list.append(sku_id)

    # 将cookie的购物车合并到redis中
    pl = redis_conn.pipeline()
    # hmset key field value 同时将多个 field-value 域值对设置到哈希表 key 中
    # hmset(name, mapping)  形成最终的一个字典即可
    pl.hmset('cart_%s' % user.id, cart)

    # selected_sku_id_list = [1,2,3,4,]
    # pl.sadd('cart_selected_%s' % user.id, 1, 2, 3, 4)
    # **能够解开字典，*可以解开列表或者元组
    pl.sadd('cart_selected_%s' % user.id, *selected_sku_id_list)

    pl.execute()

    # 清除cookie中的购物车数据
    response.delete_cookie('cart')

    return response
