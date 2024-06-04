from typing import Annotated, Literal, Optional

from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException
from odmantic import AIOEngine

from models.application import Application
from models.oidc.payloads import AccessToken, IdToken, RefreshToken
from utils.database import require_engine
from utils.dependencies.application import \
    require_application_from_app_id_and_secret

router = APIRouter(prefix='/authentication', tags=['验证'])


@router.post(
    '/signin',
    name='用户凭据登录',
    description='此端点为基于直接 API 调用形式的登录端点，适用于你需要自建登录页面的场景，请自行保证其安全性。',
    responses={
        200: {
            'description': '登录成功',
            'content': {
                'application/json': {
                    'example': {
                        'scope': 'openid profile',
                        'access_token': '<access_token>',
                        'id_token': '<id_token>',
                        'refresh_token': '<refresh_token>'
                    }
                }
            }
        },
        404: {
            'description': '用户不存在',
            'content': {
                'application/json': {
                    'example': {
                        'detail': '用户不存在'
                    }
                }
            }
        },
        400: {
            'description': '密码不能为空，当验证方式为 PASSWORD 且未传入 password 参数时抛出',
            'content': {
                'application/json': {
                    'example': {
                        'detail': '密码不能为空'
                    }
                }
            }
        },
        401: {
            'description': '密码错误',
            'content': {
                'application/json': {
                    'example': {
                        'detail': '密码错误'
                    }
                }
            }
        }
    }
)
async def signin(
    connection: Annotated[Literal['PASSWORD'], Body(description='认证方式')],
    username: Annotated[str, Body(description='用户名')],
    password: Annotated[Optional[str], Body(description='密码，当使用 PASSWORD 认证方式时必填')],
    application: Application = Depends(require_application_from_app_id_and_secret),
    engine: AIOEngine = Depends(require_engine)
):
    users = await application.get_users()
    user = next((user for user in users if user.username == username), None)

    if user is None:
        raise HTTPException(status_code=404, detail='用户不存在')

    if connection == 'PASSWORD':
        if password is None:
            raise HTTPException(status_code=400, detail='密码不能为空')

        if user.password != password:
            raise HTTPException(status_code=401, detail='密码错误')

    # 验证通过，返回 token
    access_token = AccessToken(aud=application.app_id, sub=user.id, scope='openid profile').to_jwt()
    id_token = IdToken(aud=application.app_id, sub=user.id).to_jwt()
    refresh_token = RefreshToken(id=ObjectId(), access_token=access_token, id_token=id_token, scope='openid profile')
    await refresh_token.save(engine)

    return {
        'scope': 'openid profile',
        'access_token': access_token,
        'id_token': id_token,
        'refresh_token': refresh_token.to_rtsecret()
    }
