from datetime import datetime, timedelta

import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, Request
from fastapi.security.api_key import APIKeyHeader
from odmantic import AIOEngine

from config import SECRET
from models import Application, UserPool

apikey_schema = APIKeyHeader(name='X-Application-Access-Token')


def generate_access_token(userpool: UserPool, application: Application, expries: timedelta = timedelta(days=1)):
    return jwt.encode({
        'userpool': userpool.id.__str__(),
        'application': application.id.__str__(),
        'exp': int((datetime.now() + expries).timestamp())
    }, SECRET)


def decode_access_token(access_token: str = Depends(apikey_schema)) -> dict:
    try:
        return jwt.decode(access_token, SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token 过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的Access token")
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=401, detail=str(e))


async def require_userpool_from_access_token(request: Request, access_token_decoded: dict = Depends(decode_access_token)) -> UserPool:
    engine: AIOEngine = request.app.db_engine
    return await engine.find_one(UserPool, UserPool.id == ObjectId(access_token_decoded['userpool']))


async def require_application_from_access_token(request: Request, access_token_decoded: dict = Depends(decode_access_token)) -> Application:
    engine: AIOEngine = request.app.db_engine
    return await engine.find_one(Application, Application.id == ObjectId(access_token_decoded['application']))
