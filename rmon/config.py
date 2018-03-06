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
    WX_APP_ID = 'your_wx_app_id'
    # 替换成微信公众号 app secret
    WX_SECRET = 'your_wx_secret_key'


class ProductConfig(DevConfig):
    """生产环境配置
    """
    DEBUG = False

    # sqlite 数据库文件路径
    path = os.path.join(os.getcwd(), 'rmon.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % path
