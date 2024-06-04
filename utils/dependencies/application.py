from typing import Annotated

from fastapi import Depends, HTTPException, Query
from odmantic import AIOEngine

from models import Application
from models.userpool import UserPool
from utils.database import require_engine


async def require_application_from_app_id(
    app_id: Annotated[str, Query(description="应用 ID")],
    engine: AIOEngine = Depends(require_engine)
) -> Application:
    result = await engine.find_one(UserPool, {
        'applications': {
            '$elemMatch': {
                'app_id': app_id
            }
        }
    })

    if result is None:
        raise HTTPException(status_code=404, detail="应用不存在")

    try:
        return next((app for app in result.applications if app.app_id == app_id))
    except StopIteration:
        raise HTTPException(status_code=404, detail="应用不存在")


async def require_application_from_app_id_and_secret(
    app_secret: Annotated[str, Query(description="应用密钥")],
    app: Application = Depends(require_application_from_app_id),
) -> Application:
    if app.app_secret != app_secret:
        raise HTTPException(status_code=401, detail="应用密钥不正确")

    return app

__all__ = [
    "require_application_from_app_id",
    "require_application_from_app_id_and_secret"
]
