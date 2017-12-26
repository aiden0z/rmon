""" rmon.common.errors

包含一些异常类型。
"""

class RestError(Exception):
    """异常基类
    """

    def __init__(self, code, message):
        """初始化异常

        Aargs:
            code (int): http 状态码
            message (str): 错误信息
        """
        self.code = code
        self.message = message
        super(RestError, self).__init__()


class RedisConnectError(RestError):
    pass


class InvalidTokenError(RestError):
    pass


class AuthenticationError(RestError):
    pass

