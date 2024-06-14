from typing import Literal

from fastapi import Depends, HTTPException
from odmantic import AIOEngine, Model
from pydantic import field_validator

from utils.database import require_engine


class Application(Model):
    name: str
    slug: str
    app_id: str
    app_secret: str

    redirect_uris: list[str] = []
    auth_protocol: Literal['OIDC']

    async def get_users(self, engine: AIOEngine = Depends(require_engine)):
        from .userpool import UserPool

        up = await engine.find_one(UserPool, {
            'applications': {
                '$elemMatch': {
                    'app_id': self.app_id,
                }
            }
        })

        if up is None:
            raise HTTPException(404, '找不到该应用')

        return up.users

    @field_validator('redirect_uris')
    @classmethod
    def redirect_url_must_https(cls, v: list[str]):
        if not all(uri.startswith('https') for uri in v):
            raise ValueError('redirect_uri 必须是 HTTPS URL')
