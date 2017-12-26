""" tests.views.test_server

测试 Redis 服务器相关所有 API
"""

import json
from flask import url_for

from rmon.models import Server

from tests.base import TestCase

class TestServerList(TestCase):
    """测试 Redis 服务器列表 API
    """

    endpoint = 'api.server_list'

    def test_get_servers(self, server, client, admin):
        """获取 Redis 服务器列表
        """

        resp = client.get(url_for(self.endpoint), headers=self.token_header(admin))

        # RestView 视图基类会设置 HTTP 头部 Content-Type 为 json
        assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'
        # 访问成功后返回状态码 200 OK
        assert resp.status_code == 200

        servers = resp.json

        # 由于当前测试环境中只有一个 Redis 服务器，所以返回的数量为 1
        assert len(servers) == 1

        h = servers[0]
        assert h['name'] == server.name
        assert h['description'] == server.description
        assert h['host'] == server.host
        assert h['port'] == server.port
        assert 'updated_at' in h
        assert 'created_at' in h

    def test_create_server_success(self, client, admin):
        """测试创建 Redis 服务器成功
        """
        # 数据库中没有记录
        assert Server.query.count() == 0

        # 用于创建 Redis 服务器的参数
        data = {
            'name': 'Redis测试服务器',
            'description': '这是一台这是服务器',
            'host': '127.0.0.1'
        }

        # 通过 '/servers/' 接口创建 Redis 服务器
        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data),
                           headers=self.token_header(admin))

        # 创建 Redis 服务器成功, 返回状态码 201
        assert resp.status_code == 201
        assert resp.json == {'ok': True}

        # 成功写入数据库
        assert Server.query.count() == 1
        server = Server.query.first()
        assert server is not None
        for key in data:
            assert getattr(server, key) == data[key]

    def test_create_server_failed_with_invalid_host(self, client, admin):
        """无效的服务器地址导致创建 Redis 服务器失败
        """
        # 地址无效时，会返回错误
        errors = {'message': 'String does not match expected pattern.', 'ok': False}

        # 用于创建 Redis 服务器的参数
        data = {
            'name': 'Redis测试服务器',
            'description': '这是一台这是服务器',
            # 无效的 IP 地址
            'host': '127.0.0.1234'
        }

        # 通过 '/servers/' 接口创建 Redis 服务器
        headers = self.token_header(admin)
        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data),
                           headers=headers)
        assert resp.status_code == 400
        assert resp.json == errors

    def test_create_server_failed_with_duplciate_server(self, server, client, admin):
        """创建重复的服务器时将失败
        """

        # 创建失败时返回的错误
        errors = {'message': 'redis server already exist', 'ok': False}

        data = {
            'name': server.name,
            'description': '重复的 Redis 服务器',
            'host': '127.0.0.1'
        }

        # 通过 '/servers/' 接口创建 Redis 服务器
        headers = self.token_header(admin)
        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data),
                           headers=headers)
        assert resp.status_code == 400
        assert resp.json == errors


class TestServerDetail(TestCase):
    """测试 Redis 服务器详情 API
    """

    endpoint = 'api.server_detail'

    def test_get_server_success(self, server, client, admin):
        """测试获取 Redis 服务器详情
        """

        url = url_for(self.endpoint, object_id=server.id)

        headers = self.token_header(admin)
        resp = client.get(url, headers=headers)

        assert resp.status_code == 200

        data = resp.json
        for key in ('name', 'description', 'host', 'port'):
            assert data[key] == getattr(server, key)

    def test_get_server_failed(self, client, admin):
        """获取不存在的 Redis 服务器详情失败
        """
        errors = {'ok': False, 'message': 'object not exist'}
        server_not_exist = 100
        url = url_for(self.endpoint, object_id=server_not_exist)

        headers = self.token_header(admin)
        resp = client.get(url, headers=headers)

        # Redis 服务器不存在时返回 404
        assert resp.status_code == 404
        assert resp.json == errors

    def test_update_server_success(self, server, client, admin):
        """更新 Redis 服务器成功
        """

        data = {'name': '更新后的服务器'}

        assert server.name != data['name']

        assert Server.query.count() == 1

        headers = self.token_header(admin)
        # 通过 '/servers/<int:object_id>' 接口更新 Redis 服务器
        resp = client.put(url_for(self.endpoint, object_id=server.id),
                          data=json.dumps(data),
                          headers=headers)

        assert resp.status_code == 200

        # 成功更新名称
        assert server.name == data['name']

    def test_update_server_success_with_duplicate_server(self, server, client, admin):
        """更新服务器名称为其他同名服务器名称时失败
        """
        errors = {'message': 'redis server already exist', 'ok': False}

        assert Server.query.count() == 1
        # 先创建 Redis 服务器
        second_server = Server(name='second_server', description='test',
                               host='192.168.0.1', port=6379)
        second_server.save()
        assert Server.query.count() == 2

        # 尝试将 second_server 的名称更新成和 server 一致，将会失败
        data = {'name': server.name}

        # 通过 '/servers/<int:object_id>' 接口更新 Redis 服务器
        headers = self.token_header(admin)
        resp = client.put(url_for(self.endpoint, object_id=second_server.id),
                          data=json.dumps(data),
                          headers=headers)

        assert resp.status_code == 400
        assert resp.json == errors

    def test_delete_success(self, server, client, admin):
        """删除 Redis 服务器成功
        """

        assert Server.query.count() == 1

        headers = self.token_header(admin)
        resp = client.delete(url_for(self.endpoint, object_id=server.id),
                             headers=headers)

        assert resp.status_code == 204
        assert Server.query.count() == 0

    def test_delete_failed_with_host_not_exist(self, client, admin):
        """删除不存在的 Redis 服务器失败
        """
        errors = {'ok': False, 'message': 'object not exist'}

        server_not_exist = 100
        assert Server.query.get(server_not_exist) is None

        headers = self.token_header(admin)
        resp = client.delete(url_for(self.endpoint, object_id=server_not_exist),
                             headers=headers)

        assert resp.status_code == 404
        assert resp.json == errors


class TestServerMetrics(TestCase):
    """测试 Redis 监控信息 API
    """

    endpoint = 'api.server_metrics'

    def test_get_metrics_success(self, server, client, admin):
        """成功获取 Redis 服务器监控信息
        """

        headers = self.token_header(admin)
        resp = client.get(url_for(self.endpoint, object_id=server.id),
                          headers=headers)

        assert resp.status_code == 200
        metrics = resp.json

        # refer https://redis.io/commands/INFO
        assert 'total_commands_processed' in metrics
        assert 'used_cpu_sys' in metrics
        assert 'used_memory' in metrics

    def test_get_metrics_failed_with_server_not_exist(self, client, admin):
        """获取不存在的 Redis 服务器监控信息失败
        """
        errors = {'ok': False, 'message': 'object not exist'}

        server_not_exist = 100
        assert Server.query.get(server_not_exist) is None

        headers = self.token_header(admin)
        resp = client.get(url_for(self.endpoint, object_id=server_not_exist),
                          headers=headers)

        assert resp.status_code == 404
        assert resp.json == errors

