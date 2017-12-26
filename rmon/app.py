""" rmon.app

该模块主要实现了 app 创建函数
"""
import os
from flask import Flask

from rmon.views import api
from rmon.models import User
from rmon.extensions import db
from rmon.wx import wx_dispatcher
from rmon.config import DevConfig, ProductConfig


def create_app(config=None):
    """ 创建并初始化 Flask app

    Args:
        config(dict): 配置字典

    Returns:
        app (object): Flask App 实例
    """

    app = Flask('rmon')

    # 根据环境变量加载开发环境或生产环境配置
    env = os.environ.get('RMON_ENV')

    if env in ('pro', 'prod', 'product'):
        app.config.from_object(ProductConfig)
    else:
        app.config.from_object(DevConfig)

    # 从环境变量 RMON_SETTINGS 指定的文件中加载配置
    app.config.from_envvar('RMON_SETTINGS', silent=True)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 从 config 参数更新配置
    if config is not None:
        app.config.update(config)

    # 注册 Blueprint
    app.register_blueprint(api)
    # 初始化数据库
    db.init_app(app)

    # 初始化微信消息处理器
    wx_dispatcher.init_app(app)

    # 如果是开发环境则创建所有数据库表
    if app.debug and not app.testing:
        with app.app_context():
            db.create_all()
            name, password = User.create_administrator()
            app.logger.debug('create administrator name/password %s/%s', name, password)
    return app
