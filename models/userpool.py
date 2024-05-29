from odmantic import Model

from .application import Application
from .resource import Resource
from .user import User


class UserPool(Model):
    name: str
    description: str
    users: list[User]
    applications: list[Application]
    resources: list[Resource]
