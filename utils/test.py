import contextlib

import httpx
from asgi_lifespan import LifespanManager

from main import create_app


@contextlib.asynccontextmanager
async def local_client():
    app = create_app()
    async with LifespanManager(app) as manager:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=manager.app),
            base_url="http://app.invalid"
        ) as client:
            yield client
