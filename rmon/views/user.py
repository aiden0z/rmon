""" rmon.views.user

实现所有的用户管理功能
"""
from flask import request, g

from rmon.common.rest import RestView
from rmon.common.errors import RestError
from rmon.models import User, UserSchema

from .decorators import ObjectMustBeExist, TokenAuthenticate

# TODO 实现解绑用户微信账户的 API

class UserList(RestView):
    """Redis 服务器列表
    """

    method_decorators = (TokenAuthenticate(), )

    def get(self):
        """获取 Redis 列表
        """
        servers = User.query.all()
        return UserSchema().dump(servers, many=True).data

    def post(self):
        """创建 Redis 实例
        """
        data = request.get_json()
        user, errors = UserSchema().load(data)
        if errors:
            return errors, 400
        user.save()
        return {'ok': True}, 201


class UserDetail(RestView):
    """ Redis 服务器列表
    """

    method_decorators = (TokenAuthenticate(), ObjectMustBeExist(User))

    def get(self, object_id):
        """
        """
        data, _ = UserSchema().dump(g.instance)
        return data

    def put(self, object_id):
        """更新服务器
        """
        schema = UserSchema(context={'instance': g.instance})
        data = request.get_json()
        server, errors = schema.load(data, partial=True)
        if errors:
            return errors, 400
        server.save()
        return {'ok': True}

    def delete(self, object_id):
        """删除服务器
        """
        # 删除服务器时候需要判断当时是否还有没有管理员账户
        if User.query.filter(User.id!=g.instance.id).count() == 0:
            raise RestError(400, 'must have one administrator')

        g.instance.delete()
        return {'ok': True}, 204
