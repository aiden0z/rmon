""" tests.fixtures

定义了所有的 fixture
"""

import pytest

from rmon.app import create_app
from rmon.models import Server
from rmon.models import User
from rmon.extensions import db as database

PASSWORD = '123456'


@pytest.fixture
def app():
    """ Flask app
    """
    config ={
        'TESTING': True
    }
    return create_app(config)


@pytest.yield_fixture
def db(app):
    """数据库
    """
    with app.app_context():
        database.create_all()
        yield database
        database.drop_all()


@pytest.yield_fixture
def client(app):
    """测试客户端
    """
    with app.test_client() as client:
        yield client


@pytest.fixture
def server(db):
    """测试 Redis 服务器记录
    """
    server = Server(name='redis_test', description='this is a test record',
             host='127.0.0.1', port='6379')
    server.save()
    return server


@pytest.fixture
def user(db):
    """测试普通用户记录
    """
    user = User(name='test_user', email='test@rmon.com', is_admin=False)
    user.password = PASSWORD
    user.save()
    return user

@pytest.fixture
def admin(db):
    """测试管理员用户记录
    """
    user = User(name='admin', email='admin@rmon.com', is_admin=True)
    user.password = PASSWORD
    user.save()
    return user

