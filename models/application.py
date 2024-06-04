from typing import Literal

from fastapi import Depends, HTTPException
from odmantic import AIOEngine, Model

from utils.database import require_engine


class Application(Model):
    name: str
    slug: str
    app_id: str
    app_secret: str

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
