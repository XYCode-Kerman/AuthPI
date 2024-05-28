import contextlib
import httpx
from asgi_lifespan import LifespanManager
from pytest import mark

from main import create_app


@contextlib.asynccontextmanager
async def _client():
    app = create_app()
    async with LifespanManager(app) as manager:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=manager.app),
            base_url="http://app.invalid"
        ) as client:
            yield client


@mark.asyncio
async def test_ping():
    app = create_app()
    async with _client() as client:
        resp = await client.get('http://app.invalid/ping')

        assert resp.status_code == 200
        assert resp.json() == 'pong'
