""" tests.views.test_token_auth

测试基于 token 的认证功能
"""

from flask import url_for

from tests.base import TestCase

class TestTokenAuth(TestCase):
    """测试 API 认证功能

    通过获取服务器列表 API 测试认证功能
    """

    endpoint = 'api.server_list'

    def test_auth_success(self, client, admin):
        """ token 正确时 API 返回 HTTP 200 状态码
        """

        resp = client.get(url_for(self.endpoint), headers=self.token_header(admin))

        # 访问成功后返回状态码 200 OK
        assert resp.status_code == 200


    def test_auth_failed_with_no_token(self, client):
        """ 没有 Authorization 头部时认证失败
        """

        resp = client.get(url_for(self.endpoint))

        assert resp.status_code == 401
        assert resp.json == {'ok': False, 'message': 'token not found'}

    def test_auth_failed_with_invalid_header(self, client):
        """ 无效的 token header

        token 必须在 Authorization 头部中，且为 `JWT <token_value>` 的形式
        """

        # token
        invalid_headers = {'Authorization': 'Bear'}

        resp = client.get(url_for(self.endpoint), headers=invalid_headers)

        assert resp.status_code == 401
        assert resp.json == {'ok': False, 'message': 'invalid token header'}

    def test_auth_failed_with_token_missing(self, client):
        """token 丢失导致认证失败
        """

        missing_header = {'Authorization': 'JWT'}
        resp = client.get(url_for(self.endpoint), headers=missing_header)

        assert resp.status_code == 401
        assert resp.json == {'ok': False, 'message': 'token missing'}

    def test_auth_failed_with_not_admin(self, client, user):
        """非管理员认证失败
        """
        header = self.token_header(user)
        resp = client.get(url_for(self.endpoint), headers=header)

        assert resp.status_code == 403
        assert resp.json == {'ok': False, 'message': 'no permission'}

