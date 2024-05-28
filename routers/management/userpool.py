from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request

from models import UserPool
from utils.dependencies.management import require_super_user

router = APIRouter(prefix='/userpool', tags=['用户池'], dependencies=[Depends(require_super_user)])


@router.get(
    '/',
    name='用户池列表',
    description='获取用户池列表',
    response_model=list[UserPool]
)
async def get_userpool_list(request: Request):
    engine = request.app.db_engine
    return await engine.find(UserPool)


@router.get(
    '/{userpool_id}',
    name='用户池详情',
    description='获取用户池详情',
    response_model=UserPool
)
async def get_userpool_detail(userpool_id: str, request: Request):
    engine = request.app.db_engine
    userpool = await engine.find_one(UserPool, UserPool.id == ObjectId(userpool_id))

    return userpool


@router.post(
    '/',
    name='创建用户池',
    description='创建用户池',
    response_model=UserPool
)
async def create_user_pool(userpool: UserPool, request: Request):
    engine = request.app.db_engine
    return await engine.save(userpool)


@router.put(
    '/{userpool_id}',
    name='更新用户池',
    description='更新用户池',
    response_model=UserPool,
    responses={
        404: {
            'description': '用户池不存在',
            'content': {
                'application/json': {
                    'example': {'detail': '用户池不存在'}
                }
            }
        }
    }
)
async def update_user_pool(userpool_id: str, userpool: UserPool, request: Request):
    engine = request.app.db_engine
    userpool = await engine.find_one(UserPool, UserPool.id == ObjectId(userpool_id))

    if userpool is None:
        raise HTTPException(status_code=404, detail="用户池不存在")

    userpool.model_update(userpool)
    return await engine.save(userpool)


@router.delete(
    '/{userpool_id}',
    name='删除用户池',
    description='删除用户池',
    responses={
        404: {
            'description': '用户池不存在',
            'content': {
                'application/json': {
                    'example': {'detail': '用户池不存在'}
                }
            }
        }
    }
)
async def delete_user_pool(userpool_id: str, request: Request):
    engine = request.app.db_engine
    return await engine.remove(UserPool, UserPool.id == ObjectId(userpool_id))
