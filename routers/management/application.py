from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from database import engine
from models import Application, UserPool
from utils.auth.token import generate_access_token
from utils.dependencies.management import require_super_user, require_userpool

router = APIRouter(prefix='/{userpool_id}', tags=['应用', '管理'])


@router.get(
    '/',
    name='获取应用列表',
    response_model=list[Application],
    dependencies=[Depends(require_super_user)]
)
async def get_applications(userpool: UserPool = Depends(require_userpool)):
    return [x.model_copy(update={'app_secret': 'hidden'}) for x in userpool.applications]


@router.get(
    '/{application_id}/access-token',
    name='获取应用访问令牌',
    response_model=str
)
async def get_application_access_token(application_id: str, userpool: UserPool = Depends(require_userpool)):
    applications = [
        x
        for x in userpool.applications
        if x.id == ObjectId(application_id)
    ]

    if applications.__len__() == 0:
        raise HTTPException(status_code=404, detail="应用不存在")

    return generate_access_token(userpool, applications[0])


@router.post(
    '/',
    name='创建应用',
    response_model=Application
)
async def create_application(application: Application, userpool: UserPool = Depends(require_userpool)):
    userpool.applications.append(application)

    return (await engine.save(userpool)).applications[-1]


@router.put(
    '/{application_id}',
    name='更新应用',
    response_model=Application,
    responses={
        404: {
            'description': '应用不存在',
            'content': {
                'application/json': {
                    'example': {'detail': '应用不存在'}
                }
            }
        }
    }
)
async def update_application(
    application_id: str,
    updated_application: Application,
    userpool: UserPool = Depends(require_userpool)
):
    application = next((x for x in userpool.applications if x.id == ObjectId(application_id)), None)
    if application is None:
        raise HTTPException(status_code=404, detail="应用不存在")

    application.model_update(updated_application)

    await engine.save(userpool)
    return application


@router.delete(
    '/{application_id}',
    name='删除应用',
    responses={
        404: {
            'description': '应用不存在',
            'content': {
                'application/json': {
                    'example': {'detail': '应用不存在'}
                }
            }
        }
    }
)
async def delete_application(application_id: str, userpool: UserPool = Depends(require_userpool)):
    application = next((x for x in userpool.applications if x.id == ObjectId(application_id)), None)
    if application is None:
        raise HTTPException(status_code=404, detail="应用不存在")

    userpool.applications.remove(application)
    await engine.save(userpool)
    return {"detail": "应用已删除"}
