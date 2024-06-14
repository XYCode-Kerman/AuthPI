import hashlib
from typing import Annotated, Any, Literal, Optional

from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from odmantic import AIOEngine

from models.application import Application
from models.oidc.payloads import (AccessToken, AuthorizationCode, CSRFToken,
                                  IdToken, RefreshToken)
from utils.database import require_engine
from utils.dependencies.application import (
    require_application_from_app_id,
    require_application_from_app_id_and_secret)

router = APIRouter(prefix='/authentication', tags=['验证'])
templates = Jinja2Templates(directory="templates")


@router.get(
    '/auth',
    name='标准 OIDC(OAuth2.0) 验证方法',
    description='此端点为标准 OIDC(OAuth2.0) 验证方法，需要配置回调 URI 等信息。\n注意：本请求直接返回一个 HTML 页面，在其中进行登录，然后会自动回调到 redirect_uri。',
    responses={
        200: {'description': '成功返回 HTML 页面'},
    },
    response_class=HTMLResponse
)
def auth(
    request: Request,
    scope: Annotated[str, Query(description='授权范围')],
    state: Annotated[str, Query(description='一个随机字符串，用于防范 CSRF 攻击，如果重定向 URL 中的 state 和请求时不同，说明受到攻击')],
    redirect_uri: Annotated[str, Query(description='重定向 URI，必须是 HTTPS')],
    response_type: Annotated[Literal['code', 'implicit'], Query(description='响应类型')] = 'code',
    nonce: Annotated[Optional[str], Query(description='防范重放攻击的字符串，`implicit` 模式下必填')] = None,
    response_mode: Annotated[Literal['query', 'fragment'], Query(description='响应模式，query 表示包含在重定向 URL 中，fragment 表示包含在重定向 URL Hash 中。\nimplicit 模式下应该使用 fragment 模式，因为 URL Hash 不会被发送到服务器。')] = 'query',  # noqa: E501
    application: Application = Depends(require_application_from_app_id),
):
    # 重定向 URI 必须是 HTTPS 且配置在 application 中
    if not redirect_uri.startswith('https'):
        raise HTTPException(400, '重定向 URI 必须使用 HTTPS')
    print(application.redirect_uris)
    # if redirect_uri not in application.redirect_uris:
    #     raise HTTPException(400, '重定向 URI 未在应用中配置')

    # nonce 在 implicit 下必填
    if response_type == 'implicit' and nonce is None:
        raise HTTPException(400, 'nonce 在 implicit 模式下必填')

    return templates.TemplateResponse(
        request=request,
        name='auth.html',
        context={
            'application': application,
            'response_type': response_type,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state,
            'nonce': nonce,
            'response_mode': response_mode,
            'csrf_token': CSRFToken().to_jwt()
        }
    )


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


@router.get(
    '/verify/user-password-to-code',
    name='内部接口，验证用户名和密码是否正确并签发授权码',
    description='用于验证用户名和密码是否正确，自行按照如下代码（或其的等价形式）将用户名和密码进行哈希后发至服务端，发送至本接口进行验证。\n```python\nsha256(f"{username}:{password}".encode("utf-8")).hexdigest()',  # noqa: E501
    response_model=Any,
)
async def verify_user_password(
    digest: Annotated[str, Query(description='用户名和密码的哈希值')],
    scope: Annotated[str, Query(description='OIDC 授权范围')],
    csrf_token: Annotated[str, Query(description='CSRF Token，用于防止来自 AuthPI 外部的调用')],
    engine: AIOEngine = Depends(require_engine),
    application: Application = Depends(require_application_from_app_id),
):
    # 验证 CSRF Token
    CSRFToken.verify(csrf_token)

    cond = (
        x
        for x in await application.get_users(engine)
        if hashlib.sha256(f'{x.username}:{x.password}'.encode('utf-8')).hexdigest() == digest
    )

    user = next(cond, None)

    if user is None:
        raise HTTPException(status_code=404, detail='用户不存在')

    code = AuthorizationCode(
        id=ObjectId(),
        application=application,
        scope=scope,
        user=user,
    )

    print(code.code)
    await engine.save(code)

    return code.code
