""" rmon.views.host

实现了所有的视图控制器
"""

from flask import request, g

from rmon.common.rest import RestView
from rmon.models import Server, ServerSchema

from .decorators import ObjectMustBeExist, TokenAuthenticate


class ServerList(RestView):
    """Redis 服务器列表
    """

    method_decorators = (TokenAuthenticate(), )

    def get(self):
        """获取 Redis 列表
        """
        servers = Server.query.all()
        return ServerSchema().dump(servers, many=True).data

    def post(self):
        """创建 Redis 实例
        """
        data = request.get_json()
        server, errors = ServerSchema().load(data)
        if errors:
            return errors, 400
        server.ping()
        server.save()
        return {'ok': True}, 201


class ServerDetail(RestView):
    """ Redis 服务器列表
    """

    method_decorators = (TokenAuthenticate(), ObjectMustBeExist(Server))

    def get(self, object_id):
        """
        """
        data, _ = ServerSchema().dump(g.instance)
        return data

    def put(self, object_id):
        """更新服务器
        """
        schema = ServerSchema(context={'instance': g.instance})
        data = request.get_json()
        server, errors = schema.load(data, partial=True)
        if errors:
            return errors, 400
        server.save()
        return {'ok': True}

    def delete(self, object_id):
        """删除服务器
        """
        g.instance.delete()
        return {'ok': True}, 204


class ServerMetrics(RestView):
    """获取服务器监控信息
    """
    method_decorators = (TokenAuthenticate(), ObjectMustBeExist(Server))

    def get(self, object_id):
        """获取监控信息
        TODO 如何限制访问频率
        """
        return g.instance.get_metrics()


class ServerCommand(RestView):
    """执行命令
    """

    method_decorators = (TokenAuthenticate(), ObjectMustBeExist(Server))

    def post(self, object_id):
        """执行 Redis 命令
        TODO 命令参数如何解析
        """
        pass
