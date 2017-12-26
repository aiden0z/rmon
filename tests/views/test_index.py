""" tests.views.index

测试首页
"""
from flask import url_for


class TestIndex:
    """测试首页

    首页需要渲染模板
    """

    endpoint = 'api.index'

    def test_index(self, client):
        """测试首页
        """

        resp = client.get(url_for(self.endpoint))

        assert resp.status_code == 200

        # 模板渲染成功并返回
        assert b'<div id="app"></div>' in resp.data

