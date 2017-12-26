""" rmon.config

rmon 配置文件
"""

import os

class DevConfig:
    """开发环境配置
    """

    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY ='OQR!YuiIZ0K5!NmqI1zy@S7x&ac5zJ9DAQhb'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    WX_TOKEN = 'shiyanlou-rmon'
    # 替换微信公众号  app id
    WX_APP_ID = 'wx7e07491f3a9329d4'
    # 替换成微信公众号 app secret
    WX_SECRET = 'c6348148c9655c866dfd872139ba2591'


class ProductConfig(DevConfig):
    """生产环境配置
    """
    DEBUG = False

    # sqlite 数据库文件路径
    path = os.path.join(os.getcwd(), 'rmon.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % path
