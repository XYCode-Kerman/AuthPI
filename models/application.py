from typing import Literal

from odmantic import Model


class Application(Model):
    name: str
    slug: str
    app_id: str
    app_secret: str

    auth_protocol: Literal['OIDC']
