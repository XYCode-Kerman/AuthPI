from fastapi.testclient import TestClient
from pytest import mark

from main import app


@mark.asyncio
async def test_ping():
    with TestClient(app=app) as client:
        resp = client.get('/ping')

        assert resp.status_code == 200
        assert resp.json() == 'pong'
