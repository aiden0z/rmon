""" tests.views.test_auth

登录认证功能测试
"""

import json
from flask import url_for

from rmon.models import User
from tests.fixtures import PASSWORD


class TestAuth:
    """测试登录功能

    登录成功后将获取到用于访问各项 API 的 token
    """

    endpoint = 'api.login'

    def test_login_success(self, client, admin):
        """登录成功
        """

        data = {'name': admin.name, 'password': PASSWORD}

        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data),
                           headers={'Content-Type':'application/json; utf-8'})

        assert resp.status_code == 200
        assert resp.json['ok'] == True

        # 获取到的 token 成功验证
        u = User.verify_token(resp.json['token'])

        assert u == admin

    def test_normal_user_login_failed(self, client, user):
        """普通用户登录失败
        """

        data = {'name': user.name, 'password': PASSWORD}

        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data),
                           headers={'Content-Type':'application/json; utf-8'})

        assert resp.status_code == 403
        assert resp.json == {'ok': False, 'message': 'administrator required'}

    def test_login_failed_with_no_password(self, client, user):
        """登录失败
        """

        data = {'password': PASSWORD}

        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data),
                           headers={'Content-Type':'application/json; utf-8'})

        assert resp.status_code == 403
        assert resp.json == {'ok': False, 'message': 'user name or password required'}
