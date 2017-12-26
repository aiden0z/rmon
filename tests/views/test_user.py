""" tests.views.test_user

测试用户管理 API
"""

import json
from flask import url_for

from rmon.models import User

from tests.base import TestCase


class TestUserList(TestCase):
    """测试用户列表 API
    """

    endpoint = 'api.user_list'

    def test_get_users(self, client, admin):
        """获取用户列表
        """

        resp = client.get(url_for(self.endpoint), headers=self.token_header(admin))

        # RestView 视图基类会设置 HTTP 头部 Content-Type 为 json
        assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'
        # 访问成功后返回状态码 200 OK
        assert resp.status_code == 200

        users = resp.json

        # 由于当前测试环境中只有 admin 用户
        assert len(users) == 1

        h = users[0]
        assert h['name'] == admin.name
        assert h['email'] == admin.email
        assert 'updated_at' in h
        assert 'created_at' in h

    def test_create_user_success(self, client, admin):
        """测试创建用户成功
        """
        # 当前数据库只有 admin 账户
        assert User.query.count() == 1

        # 用于创建用户的数据
        data = {
            'name': 'test_user',
            'email': 'test_user@test.com',
            'password': '000000'

        }

        # 通过 '/users/' 接口创建用户
        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data),
                           headers=self.token_header(admin))

        # 创建成功, 返回状态码 201
        assert resp.status_code == 201
        assert resp.json == {'ok': True}

        # 成功写入数据库
        assert User.query.count() == 2
        user = User.query.filter_by(name=data['name']).first()
        assert user is not None
        assert user.email == data['email']

        # 创建的用户可以进行登录
        assert User.authenticate(data['name'], data['password']) == user
        assert User.authenticate(data['email'], data['password']) == user


    def test_create_user_failed_with_invalid_email(self, client, admin):
        """无效的邮件导致创建用户失败
        """
        # 地址无效时，会返回错误
        errors = {'message': 'Not a valid email address.', 'ok': False}

        # 用于创建用户的数据
        data = {
            'name': 'test_user',
            # 无效邮件
            'email': 'test_usertest.com',
            'password': '000000'

        }

        headers = self.token_header(admin)
        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data),
                           headers=headers)
        assert resp.status_code == 400
        assert resp.json == errors

    def test_create_user_failed_with_duplciate_user(self, client, admin):
        """创建重复的用户时将失败
        """

        # 创建失败时返回的错误
        errors = {'message': 'user already exist', 'ok': False}

        data = {
            'name': admin.name,
            'email': 'test_user@test.com',
            'password': '000000'

        }

        headers = self.token_header(admin)
        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data),
                           headers=headers)
        assert resp.status_code == 400
        assert resp.json == errors


class TestUserDetail(TestCase):
    """测试用户详情 API
    """

    endpoint = 'api.user_detail'

    def test_get_user_success(self, client, admin):
        """测试获取用户详情
        """

        url = url_for(self.endpoint, object_id=admin.id)

        headers = self.token_header(admin)
        resp = client.get(url, headers=headers)

        assert resp.status_code == 200

        data = resp.json
        for key in ('name', 'email', 'is_admin'):
            assert data[key] == getattr(admin, key)

    def test_get_user_failed(self, client, admin):
        """获取不存在用户失败
        """
        errors = {'ok': False, 'message': 'object not exist'}
        user_not_exist = 100
        url = url_for(self.endpoint, object_id=user_not_exist)

        headers = self.token_header(admin)
        resp = client.get(url, headers=headers)

        assert resp.status_code == 404
        assert resp.json == errors

    def test_update_user_success(self, client, admin):
        """更新用户失败
        """

        data = {'name': 'new_name'}

        assert admin.name != data['name']

        assert User.query.count() == 1

        headers = self.token_header(admin)

        # 更新用户
        resp = client.put(url_for(self.endpoint, object_id=admin.id),
                          data=json.dumps(data),
                          headers=headers)

        assert resp.status_code == 200

        # 成功更新名称
        assert admin.name == data['name']

    def test_update_user_success_with_duplicate_user(self, client, admin, user):
        """更新用户名称成功和其他用户同名时失败
        """
        errors = {'message': 'user already exist', 'ok': False}

        # 尝试将 user 的名称更新成和 admin 相同，将会失败
        data = {'name': admin.name}

        headers = self.token_header(admin)
        resp = client.put(url_for(self.endpoint, object_id=user.id),
                          data=json.dumps(data),
                          headers=headers)

        assert resp.status_code == 400
        assert resp.json == errors

    def test_delete_success(self, client, admin, user):
        """删除用户成功
        """

        assert User.query.count() == 2

        headers = self.token_header(admin)
        resp = client.delete(url_for(self.endpoint, object_id=user.id),
                             headers=headers)

        assert resp.status_code == 204
        assert User.query.count() == 1

    def test_delete_failed_with_delete_admin(self, client, admin):
        """删除唯一的管理员账户时失败
        """
        errors = {'ok': False, 'message': 'must have one administrator'}

        headers = self.token_header(admin)
        resp = client.delete(url_for(self.endpoint, object_id=admin.id),
                             headers=headers)
        assert resp.json == errors
