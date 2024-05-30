from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from odmantic import AIOEngine

from models import User, UserPool
from utils.auth.token import require_userpool_from_access_token
from utils.database import require_engine

router = APIRouter(prefix='/user', tags=['用户管理'])


@router.get(
    '/',
    name='获取用户列表',
    response_model=list[User]
)
async def get_users(userpool: UserPool = Depends(require_userpool_from_access_token),):
    return userpool.users


@router.get(
    '/{user_id}',
    name='获取用户详情',
    response_model=User,
    responses={
        404: {
            'description': '用户不存在',
            'content': {
                'application/json': {
                    'example': {'detail': '用户不存在'}
                }
            }
        }
    }
)
async def get_user(
    user_id: str,
    userpool: UserPool = Depends(require_userpool_from_access_token),
):
    user = next((u for u in userpool.users if u.id == ObjectId(user_id)), None)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post(
    '/',
    name='创建用户',
    response_model=User,
    responses={
        400: {
            "description": "用户已存在",
            "content": {
                "application/json": {
                    "example": {"detail": "用户已存在"}
                }
            }
        }
    }
)
async def create_user(
    user: User,
    userpool: UserPool = Depends(require_userpool_from_access_token),
    engine: AIOEngine = Depends(require_engine)
):
    if user.username in [x.username for x in userpool.users]:
        raise HTTPException(status_code=400, detail="用户已存在")
    userpool.users.append(user)
    await engine.save(userpool)
    return user


@router.put(
    '/{user_id}',
    name='更新用户',
    response_model=User,
    responses={
        404: {
            "description": "用户不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "用户不存在"}
                }
            }
        }
    }
)
async def update_user(
    user_id: str,
    updated_user: User,
    userpool: UserPool = Depends(require_userpool_from_access_token),
    engine: AIOEngine = Depends(require_engine)
):
    user = next((u for u in userpool.users if u.id == ObjectId(user_id)), None)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.model_update(updated_user, exclude=['id'])
    await engine.save(userpool)
    return user


@router.delete(
    '/{user_id}',
    name='删除用户',
    responses={
        404: {
            "description": "用户不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "用户不存在"}
                }
            }
        }
    }
)
async def delete_user(
    user_id: str,
    userpool: UserPool = Depends(require_userpool_from_access_token),
    engine: AIOEngine = Depends(require_engine)
):
    user = next((u for u in userpool.users if u.id == ObjectId(user_id)), None)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    userpool.users.remove(user)
    await engine.save(userpool)
    return {"detail": "用户删除成功"}
