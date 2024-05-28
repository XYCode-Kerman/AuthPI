from datetime import datetime, timedelta

import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException
from odmantic import AIOEngine

from config import SECRET
from models import Application, UserPool


def generate_access_token(userpool: UserPool, application: Application):
    return jwt.encode({
        'userpool': userpool.id.__str__(),
        'application': application.id.__str__(),
        'exp': datetime.now() + timedelta(days=1)
    }, SECRET)


def decode_access_token(access_token: str) -> dict:
    try:
        return jwt.decode(access_token, SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token 过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的Access token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


async def require_userpool_from_access_token(engine: AIOEngine, access_token_decoded: dict = Depends(decode_access_token)) -> UserPool:
    return await engine.find_one(UserPool, UserPool.id == ObjectId(access_token_decoded['userpool']))


async def require_application_from_access_token(engine: AIOEngine, access_token_decoded: dict = Depends(decode_access_token)) -> Application:
    return await engine.find_one(Application, Application.id == ObjectId(access_token_decoded['application']))
