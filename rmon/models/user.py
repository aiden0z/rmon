""" rmon.models.user

该模块实现了用户数据库模型
"""

import jwt
from datetime import datetime, timedelta
from calendar import timegm

from werkzeug import generate_password_hash, check_password_hash
from marshmallow import (Schema, fields, validate, post_load,
                         validates_schema, ValidationError)
from flask import current_app

from rmon.common.errors import InvalidTokenError, AuthenticationError
from rmon.extensions import db

from .base import BaseModel


class User(BaseModel):

    """用户模型
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    # 用户微信 ID，全局唯一
    wx_id = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    login_at = db.Column(db.DateTime)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, passwd):
        """设置密码
        """
        self._password = generate_password_hash(passwd)

    def verify_password(self, password):
        """检查密码
        """
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, identifier, password):
        """认证用户

        Args:
            identifier(str): 用户名称或者邮箱
            password(str): 用户密码

        Returns:
            object: 用户对象

        Raises:
            AuthenticationError
        """
        user = cls.query.filter(db.or_(cls.name==identifier,
                                       cls.email==identifier)).first()
        if user is None or not user.verify_password(password):
            raise AuthenticationError(403, 'authentication failed')
        return user

    def generate_token(self):
        """生成 json web token

        生成 token，有效期为 1 天，过期后十分钟内可以使用老 token 刷新获取新的
        token
        """
        # token 过期时间，默认在一天后过期
        exp = datetime.utcnow() + timedelta(days=1)
        # token 过期后十分钟内，还可以使用老 token 进行刷新 token
        refresh_exp = timegm((exp + timedelta(seconds=60 * 10)).utctimetuple())

        payload = {
            'uid': self.id,
            'is_admin': self.is_admin,
            'exp': exp,
            'refresh_exp': refresh_exp
            }

        return jwt.encode(payload, current_app.secret_key, algorithm='HS512').decode('utf-8')

    @classmethod
    def verify_token(cls, token, verify_exp=True):
        """检查验证 json web token

        Args:
            token(str): json web token
            verify_exp(bool): 是否验证 token 的过期时间

        Return:
            object: 返回用户对象

        Raise:
            InvalidTokenError
        """
        now = datetime.utcnow()

        if verify_exp:
            options = None
        else:
            options = {'verify_exp': False}

        try:
            payload = jwt.decode(token, current_app.secret_key, verify=True,
                                 algorithms=['HS512'], options=options,
                                 require_exp=True)
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(403, str(e))

        if any(('is_admin' not in payload,
                'refresh_exp' not in payload, 'uid' not in payload)):
            raise InvalidTokenError(403, 'invalid token')

        # 如果刷新时间过期，则认为 token 无效
        if payload['refresh_exp'] < timegm(now.utctimetuple()):
            raise InvalidTokenError(403, 'invalid token')

        u = User.query.get(payload.get('uid'))
        if u is None:
            raise InvalidTokenError(403, 'user not exist')
        return u

    @classmethod
    def create_administrator(cls):
        """创建管理员账户

        Returns:
            name(str): 管理员账户名称
            password(str): 管理员账户密码
        """
        name = 'admin'
        # 管理员账户名称默认为 admin
        admin = cls.query.filter_by(name=name).first()
        if admin:
            return admin.name, ''
        password = '123456'
        admin = User(name=name, email='amin@rmon.com', is_admin=True)
        admin.password = password
        admin.save()
        return name, password

    @classmethod
    def wx_id_user(cls, wx_id):
        """根据 wx_id 获取用户
        """
        return cls.query.filter_by(wx_id=wx_id).first()


class UserSchema(Schema):
    """User对象序列化类
    """
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(2, 64))
    email = fields.Email(required=True, validate=validate.Length(2, 64))
    password = fields.String(load_only=True, validate=validate.Length(2, 128))
    is_admin = fields.Boolean()
    wx_id = fields.String(dump_only=True)
    login_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_schema(self, data):
        """检查数据
        """
        instance = self.context.get('instance', None)

        user = User.query.filter(db.or_(User.name==data.get('name'),
                                        User.email==data.get('email'))).first()

        if user is None:
            return

        # 创建服务器时
        if instance is None:
            field = 'name' if user.name == data['name'] else 'email'
            raise ValidationError('user already exist', field)

        # 更新用户时
        if user != instance:
            # 判断是存在同名用户或者是同邮箱的用户
            field = 'name' if user.name == instance.name else 'email'
            raise ValidationError('user already exist', field)



    @post_load
    def create_or_update(self, data):
        """数据加载成功后自动创建 User
        """
        instance = self.context.get('instance', None)

        # 创建用户
        if instance is None:
            user = User()
        # 更新用户
        else:
            user = instance

        # FIXME 更新用户时可能覆盖用户密码
        for key in data:
            setattr(user, key, data[key])
        return user
