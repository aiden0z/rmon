""" tests.test_models

测试所有数据库模型
"""

import jwt
from datetime import datetime, timedelta
from calendar import timegm

from rmon.models import Server, User
from rmon.common.errors import (
    RedisConnectError, InvalidTokenError, AuthenticationError)

from tests.fixtures import PASSWORD

class TestServer:
    """测试 Server 相关功能
    """

    def test_save(self, db):
        """测试 Server.save 保存服务器方法
        """
        # 初始状态下，数据库中没有保存任何 Redis，所以数量为 0
        assert Server.query.count() == 0
        server = Server(name='test', host='127.0.0.1')
        # 保存到数据库中
        server.save()
        # 现在数据库中数量变为 1
        assert  Server.query.count() == 1
        # 且数据库中的记录就是之前创建的记录
        assert Server.query.first() == server

    def test_delete(self, db, server):
        """测试 Server.delete 删除服务器方法
        """
        assert Server.query.count() == 1
        server.delete()
        assert Server.query.count() == 0

    def test_ping_success(self, db, server):
        """测试 Server.ping 方法执行成功

        需要保证 Redis 服务器监听在 127.0.0.1:6379 地址
        """
        assert server.ping() is True

    def test_ping_failed(self, db):
        """测试 Server.ping 方法执行失败

        Server.ping 方法执行失败时，会抛出 RedisConnectError 异常
        """

        # 没有 Redis 服务器监听在 127.0.0.1:6399 地址, 所以将访问失败
        server = Server(name='test', host='127.0.0.1', port=6399)

        try:
            server.ping()
        except RedisConnectError as e:
            assert e.code == 400
            assert e.message == 'redis server %s can not connected' % server.host

    def test_get_metrics_success(self, server):
        """测试 Server.get_metrics 方法执行成功
        """

        metrics = server.get_metrics()

        # refer https://redis.io/commands/INFO
        assert 'total_commands_processed' in metrics
        assert 'used_cpu_sys' in metrics
        assert 'used_memory' in metrics

    def test_get_metrics_failed(self, server):
        """测试 Server.get_metrics 方法执行失败
        """

        # 没有 Redis 服务器监听在 127.0.0.1:6399 地址, 所以将访问失败
        server = Server(name='test', host='127.0.0.1', port=6399)

        try:
            server.get_metrics()
        except RedisConnectError as e:
            assert e.code == 400
            assert e.message == 'redis server %s can not connected' % server.host


class TestUser:
    """测试 User
    """

    def test_verify_password(self, user):
        """测试 User.verify_password 实例方法
        """
        assert user.verify_password(PASSWORD)

        wrong_password = PASSWORD + '0'
        assert not user.verify_password(wrong_password)

    def test_authenticate(self, user):
        """测试 User.authenticate 类方法
        """
        assert User.authenticate(user.name, PASSWORD)
        assert user.authenticate(user.email, PASSWORD)

        wrong_password = PASSWORD + '0'

        try:
            User.authenticate(user.name, wrong_password)
        except AuthenticationError as e:
            assert e.code == 403
            assert e.message == 'authentication failed'

        try:
            User.authenticate(user.email, wrong_password)
        except AuthenticationError as e:
            assert e.code == 403
            assert e.message == 'authentication failed'

    def test_generate_token(self, user, app):
        """测试 User.generate_token 方法
        """

        now = timegm(datetime.utcnow().utctimetuple())
        token = user.generate_token()

        payload = jwt.decode(token, verify=False)

        assert payload['uid'] == user.id
        assert payload['is_admin'] == user.is_admin
        assert 'refresh_exp' in payload
        assert 'exp' in payload

        # 生成的 token 有效期为一天
        assert payload['exp'] - now == 24 * 3600
        # token 过期后十分钟内，还可以使用老 token 进行刷新 token
        assert payload['refresh_exp'] - now == 24 * 3600 + 10 * 60
        u = User.verify_token(token)
        assert u == user


    def test_verify_token(self, user):
        """测试 User.verify_token 类方法
        """
        # 成功验证 token
        token = user.generate_token()
        # 验证 token 成功后会返回 User 对象
        u = User.verify_token(token)
        assert user == u

    def test_verify_token_failed(self, user, app):
        """测试 User.verify_token 验证 token 时失败
        """

        algorithm = 'HS512'

        # token 验证失败
        invalid_token = user.generate_token() + '0'

        try:
            User.verify_token(invalid_token)
        except InvalidTokenError as e:
            assert e.code == 403
            assert 'Signature' in e.message

        # token 指定的用户不存在
        exp = datetime.utcnow() + timedelta(days=1)
        # token 过期后十分钟内，还可以使用老 token 进行刷新 token
        refresh_exp = timegm((exp + timedelta(seconds=60 * 10)).utctimetuple())

        # 用户步存在
        user_not_exist = 100
        payload = {
            'uid': user_not_exist,
            'is_admin': False,
            'exp': exp,
            'refresh_exp': refresh_exp
            }

        # 用户不存在
        try:
            User.verify_token(jwt.encode(payload, app.secret_key, algorithm=algorithm))
        except InvalidTokenError as e:
            assert e.code == 403
            assert e.message == 'user not exist'

        payload = {'exp': exp}
        try:
            User.verify_token(jwt.encode(payload, app.secret_key, algorithm=algorithm))
        except InvalidTokenError as e:
            assert e.code == 403
            assert e.message == 'invalid token'

        # token 刷新时间无效
        refresh_exp = datetime.utcnow() - timedelta(days=1)

