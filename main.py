from fastapi import FastAPI

from routers import management

app = FastAPI(
    title='AuthPI',
    summary='开放的身份云API实现，参考了Authing',
    description='AuthPI是一款参照了Authing API设计的**开源的**用户管理系统。如**用户池、应用、联邦认证、ZTA**的相关概念与Authing十分相似。',
    version='0.0.1-infdev.1',
    license_info={
        'name': 'MIT License & Anti-996 License',
        'url': 'https://github.com/XYCode-Kerman/AuthPI/blob/main/LICENSE.md'
    }
)

app.openapi_tags = [
    {'name': '杂项', 'description': '用于检测服务可用性或是获取一些业务无关信息'},
]

app.include_router(management.router)


@app.get(
    '/ping',
    name='Ping',
    description='返回 pong，用于测试服务是否可用。',
    tags=['杂项'],
    responses={
        200: {
            'description': 'The ping response',
            'content': {
                'application/json': {
                    'example': 'pong'
                }
            }
        }
    }
)
def ping():
    return 'pong'
