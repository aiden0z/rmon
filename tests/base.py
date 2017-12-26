""" tests.base

定义测试基类
"""


class TestCase:
    """测试基类
    """

    def token_header(self, user):
        """生成包含 jwt token 的 HTTP 头部
        """
        value = 'JWT %s' % user.generate_token()
        return {
            'Authorization': value,
            'Content-Type': 'application/json; charset=utf-8'
        }
