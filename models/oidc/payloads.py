import datetime
import secrets
from secrets import token_urlsafe
from typing import Literal, Optional

import jwt
import odmantic
from fastapi import HTTPException
from odmantic import AIOEngine, Model, Reference
from pydantic import BaseModel, Field

from config import ISSUER, SECRET
from models.application import Application
from models.user import User
from utils.security.crypto import crypt_message_with_aes


class BasicPayload(BaseModel):
    jti: str = Field(default_factory=lambda: token_urlsafe(32), description='JWT的唯一标识')
    iss: str = Field(default=ISSUER, description='签发者')
    iat: int = Field(default_factory=lambda: int(datetime.datetime.now().timestamp()), description='签发时间')
    exp: int = Field(default_factory=lambda: int(datetime.datetime.now().timestamp() +
                     datetime.timedelta(minutes=10).seconds), description='过期时间')
    nonce: str = Field(default_factory=lambda: token_urlsafe(32), description='随机数，防止重放攻击')

    def to_jwt(self):
        return jwt.encode(
            self.model_dump(mode='json'),
            SECRET,
            algorithm='HS256'
        )


class IdToken(BasicPayload):
    sub: str = Field(description='用户唯一标识，即用户的 _id')
    aud: str = Field(description='受众，填入 `app_id`')
    auth_time: Optional[None] = Field(default=None,
                                      description="auth_time参数记录用户最后认证时间，增强安全性和会话管理，支持法规遵从和用户体验。客户端请求中包含max_age或强制请求auth_time参数时，提供该参数")  # noqa: E501


class AccessToken(BasicPayload):
    aud: str = Field(description='受众，填入 `app_id`')
    sub: str = Field(description='用户唯一标识，即用户的 _id')
    scope: str = Field(description='授权范围，以空格分隔。你填不存在的 scope 也行，只不过会被 AuthPI 的内置权限系统忽略而已。')


class RefreshToken(BasicPayload, Model):
    access_token: str = odmantic.Field(description='一个 Access Token')
    expries_in: int = odmantic.Field(default=datetime.timedelta(minutes=10).seconds, description='Access Token 的过期时间，单位为秒')
    id_token: str = odmantic.Field(description='一个 ID Token')
    scope: str = odmantic.Field(
        description='AccessToken 的授权范围，以空格分隔。支持 openid 规范中定义的自带 scope 和 自定义scope。你填不存在的自定义 scope 也行，只不过会被 AuthPI 的内置权限系统忽略而已。')
    token_type: Literal['Bearer'] = odmantic.Field(default='Bearer', description='Token 类型，只能是 `Bearer`')

    async def save(self, engine: AIOEngine):
        return await engine.save(self)

    async def delete(self, engine: AIOEngine):
        return await engine.delete(self)

    def to_jwt(self):
        raise NotImplementedError('Refresh Token 不能被编码为 JWT。使用 to_rtsecret 来获取一个被服务器加密后的 RefreshToken')

    def to_rtsecret(self):
        return crypt_message_with_aes(self.model_dump_json())


class CSRFToken(BasicPayload):
    pass

    @staticmethod
    def verify(token: str):
        try:
            jwt.decode(token, SECRET, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            raise HTTPException(400, '无效的 CSRF Token')


class AuthorizationCode(Model):
    code: str = odmantic.Field(default_factory=lambda: secrets.token_hex(4), description='授权码')
    scope: str = odmantic.Field(description='授权范围，以空格分隔。你填不存在的 scope 也行，只不过会被 AuthPI 的内置权限系统忽略而已。')
    application: Application = Reference()
    user: User = Reference()
