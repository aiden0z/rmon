""" rmon.views.wx

微信相关视图控制器
"""
import hashlib

from flask import request, current_app, abort, render_template, make_response
from flask.views import MethodView
from wechatpy import parse_message

from rmon.models import User
from rmon.wx import wx_dispatcher
from rmon.common.rest import RestView


class WxView(MethodView):
    """ 微信相关视图控制器
    """

    def check_signature(self):
        """ 验证请求是否来自于微信请求
        """
        signature = request.args.get('signature')
        if signature is None:
            abort(403)

        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')

        msg = [current_app.config['WX_TOKEN'], timestamp, nonce]
        msg.sort()

        sha = hashlib.sha1()
        sha.update(''.join(msg).encode('utf-8'))

        if sha.hexdigest() != signature:
            abort(403)

    def get(self):
        """ 用于验证在微信公众号后台设置的URL
        """
        self.check_signature()
        return request.args.get('echostr')

    def post(self):
        """ 处理微信消息
        """
        self.check_signature()

        msg = parse_message(request.data)
        reply = wx_dispatcher.dispatch(msg)
        return reply.render()


class WxBind(RestView):
    """微信注册绑定账户页面
    """

    def get(self, wx_id):
        result = render_template('wx_bind.html')
        return make_response(result, 200)

    def post(self, wx_id):
        """绑定用户
        """
        data = request.get_json()
        if data is None or 'name' not in data or 'password' not in data:
            return {'ok': False, 'message': '无效用户数据'}, 400

        user = User.authenticate(data['name'], data['password'])

        if user.wx_id is not None:
            return {'ok': False, 'message': '已绑定到其他微信账户'}, 400

        user.wx_id = wx_id
        user.save()
        return {'ok': True, 'message': '绑定成功'}
