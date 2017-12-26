""" rmon.wx.dispatcher

微信消息处理逻辑
"""
from wechatpy import WeChatClient
from wechatpy.replies import BaseReply, EmptyReply

from .handlers import default_handlers


class MessageDispatcher:

    def __init__(self):
        self.handlers = []
        self.wx_client = None

    def init_app(self, app):
        """从 flask app 中初始化
        """
        self.wx_client = WeChatClient(app.config.get('WX_APP_ID'),
                                      app.config.get('WX_SECRET'))
        self.handlers = []
        for handler_class in default_handlers:
            self.register_handler(handler_class(wx_client=self.wx_client))

    def register_handler(self, handler):
        self.handlers.append(handler)

    def _reply(self, msg):
        """处理消息
        """
        for h in self.handlers:
            reply = h.handle(msg)
            if isinstance(reply, BaseReply):
                return reply
        return EmptyReply()

    def dispatch(self, msg):
        return self._reply(msg)
