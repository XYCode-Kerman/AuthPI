from pytest import mark

from utils.test import local_client


@mark.asyncio
async def test_ping():
    async with local_client() as client:
        resp = await client.get('http://app.invalid/ping')

        assert resp.status_code == 200
        assert resp.json() == 'pong'
