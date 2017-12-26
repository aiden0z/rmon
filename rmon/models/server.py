""" rmon.models.server

该模块实现了所有的 model 类以及相应的序列化类
"""

from marshmallow import (Schema, fields, validate, post_load,
                         validates_schema, ValidationError)
from redis import StrictRedis, RedisError

from rmon.common.errors import RedisConnectError
from rmon.extensions import db

from .base import BaseModel



class Server(BaseModel):
    """Redis服务器模型
    """

    __tablename__ = 'redis_server'

    id = db.Column(db.Integer, primary_key=True)
    # unique = True 设置不能有同名的服务器
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(512))
    host = db.Column(db.String(15))
    port = db.Column(db.Integer, default=6379)
    password = db.Column(db.String())

    @property
    def redis(self):
        return StrictRedis(host=self.host, port=self.port, password=self.password)

    def ping(self):
        """检查 Redis 服务器是否可以访问
        """
        try:
            return self.redis.ping()
        except RedisError:
            raise RedisConnectError(400, 'redis server %s can not connected' % self.host)

    @property
    def status(self):
        """服务器当前状态
        """
        status = 'error'
        try:
            if self.ping():
                status = 'ok'
        except RedisConnectError:
            pass
        return status

    def get_metrics(self):
        """获取 Redis 服务器监控信息

        通过 Redis 服务器指令 INFO 返回监控信息, 参考 https://redis.io/commands/INFO
        """
        try:
            # TODO 新版本的 Redis 服务器支持查看某一 setion 的信息，不必返回所有信息
            return self.redis.info()
        except RedisError:
            raise RedisConnectError(400, 'redis server %s can not connected' % self.host)


class ServerSchema(Schema):
    """Redis服务器记录序列化类
    """
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(2, 64))
    description = fields.String(validate=validate.Length(0, 512))
    # host 必须是 IP v4 地址
    host = fields.String(required=True,
                         validate=validate.Regexp(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'))
    port = fields.Integer(validate=validate.Range(1024, 65536))
    password = fields.String()
    updated_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_schema(self, data):
        """验证是否已经存在同名 Redis 服务器
        """
        if 'port' not in data:
            data['port'] = 6379

        instance = self.context.get('instance', None)

        # 由于更新服务器时通过 partial=True 加载数据，会忽略对缺失字段的验证
        # 所以需要判断 name 字段是否存在
        if 'name' not in data:
            return

        server = Server.query.filter_by(name=data['name']).first()

        if server is None:
            return

        # 更新服务器时
        if instance is not None and server != instance:
            raise ValidationError('redis server already exist', 'name')

        # 创建服务器时
        if instance is None and server:
            raise ValidationError('redis server already exist', 'name')

    @post_load
    def create_or_update(self, data):
        """数据加载成功后自动创建 Server 对象
        """
        instance = self.context.get('instance', None)

        # 创建 Redis 服务器
        if instance is None:
            return Server(**data)

        # 更新服务器
        for key in data:
            setattr(instance, key, data[key])
        return instance

