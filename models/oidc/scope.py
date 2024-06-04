from typing import Literal, Optional

from odmantic import Field, Model
from pydantic import field_validator

Resource = str
Action = str
Effect = Optional[Literal['allow', 'deny']]


class CustomScope(Model):
    name: str = Field(description='Scope 的名称，必须以 SCOPE_ 开头。对应一个 AuthPI 内置RBAC权限系统的 Role')
    description: str
    permissions: list[tuple[Resource, Action, Effect]] = Field(
        description='权限列表，每个权限由资源、操作和效果组成。对应一个 AuthPI 内置RBAC权限系统的 Permission，但是缺省 Subject 字段（使用 name 字段代替）')

    # TODO: 转为 AuthPI 内置RBAC权限系统的一个 Role
    # def to_rbac_role():

    # name 必须以 scope_ 开头
    @field_validator('name')
    @classmethod
    def name_must_start_with_SCOPE_(cls, v: str):
        if not v.startswith('SCOPE_'):
            raise ValueError('Scope 的名称必须以 SCOPE_ 开头')
        return v
