from bson import ObjectId
from fastapi import Depends, HTTPException, Request
from fastapi.security.api_key import APIKeyHeader

from config import SUPER_USER_TOKEN
from models import UserPool

superuser_token_schema = APIKeyHeader(name='su-token', description='超级用户访问令牌')


async def require_userpool(userpool_id: str, request: Request) -> UserPool:
    engine = request.app.db_engine
    return await engine.find_one(UserPool, UserPool.id == ObjectId(userpool_id))


def require_super_user(token: str = Depends(superuser_token_schema)):
    if token != SUPER_USER_TOKEN:
        raise HTTPException(status_code=403, detail="禁止访问")

    return token
