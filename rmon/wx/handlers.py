""" rmon.wx.handlers

消息处理器
"""
from wechatpy.events import SubscribeEvent
from wechatpy.messages import TextMessage
from wechatpy import create_reply

from flask import url_for

from rmon.models import User, Server


class BaseHandler:
    """ 消息处理基类
    """
    def __init__(self, wx_client=None):
        self.wx_client = wx_client

    def handle(self, message, *args, **kwargs):
        """处理消息

        Args:
            message(object):
        """
        raise NotImplementedError('must be implement handle method')


class SubscribeEventHandler(BaseHandler):
    """关注事件处理器

    当用户关注公众号时，触发的事件
    """

    def handle(self, message, *args, **kwargs):
        if not isinstance(message, SubscribeEvent):
            return
        # TODO 获取微信用户信息
        result = self.wx_client.user.get(message.source)
        print(result)
        return create_reply('欢迎关注 rmon 公众号', message)


class  EchoHandler(BaseHandler):

    def handle(self, message, *args, **kwargs):
        if not isinstance(message, TextMessage):
            return
        return create_reply(message.content, message)


class CommandHandler(BaseHandler):
    """ 使用文本命令触发的处理基类

    触发命令时必须检查用户是否已经绑定
    """

    command = ''

    def check_match(self, message):
        """检查消息是否匹配命令模式
        """
        if not isinstance(message, TextMessage):
            return False

        if not message.content.strip().lower().startswith(self.command):
            return False
        return True


class BindCommandHandler(CommandHandler):
    """绑定用户处理基类
    """

    command = 'bind'

    def handle(self, message):
        """ 执行相应的命令
        """
        # 判断命令是否匹配
        if not self.check_match(message):
            return

        # 判断用户是否已经绑定
        user = User.wx_id_user(message.source)
        if user is not None:
            return create_reply('你已绑定到 %s 用户' % user.name, message)

        # 返回绑定用户链接
        url = url_for('api.wx_bind', wx_id=message.source, _external=True)
        return  create_reply('请打开链接 %s 完成用户绑定' % url, message)


class RedisCommandHandler(CommandHandler):
    """ Redis 命令
    """

    command = 'redis'

    def handle(self, message):
        # 判断命令是否匹配
        if not self.check_match(message):
            return

        # 检查微信用户是否已经绑定到 rmon 用户
        user = User.wx_id_user(message.source)
        if not user:
            return create_reply('未绑定用户', message)
        parts = message.content.strip().split(' ')
        if len(parts) == 1:
            return create_reply('请输入子命令', message)
        if parts[1].lower() == 'ls':
            return create_reply(self.list_servers(), message)
        elif parts[1].lower() == 'del':
            return create_reply(self.delete_server(*parts[2:]), message)
        else:
            return create_reply('命令暂未实现', message)

    def list_servers(self):
        """列出所有的 Redis 服务器
        """
        content = ''
        for server in Server.query:
            item = '%s %s %s\n' % (server.name, server.host, server.status)
            content += item
        if not content:
            return '还未创建任何 Redis 服务器'
        return content

    def delete_server(self, *servers):
        """删除服务器
        """
        if len(servers) == 0:
            return '未指定 Redis 服务器名称'

        result = ''
        for name in servers:
            server = Server.query.filter_by(name=name).first()
            if server:
                server.delete()
                result += '成功删除 %s\n' % server.name
            else:
                result += '未发现 %s\n'
        return result

default_handlers = (SubscribeEventHandler, BindCommandHandler, RedisCommandHandler)
