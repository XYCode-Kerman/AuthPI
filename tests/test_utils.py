from datetime import timedelta

from fastapi import HTTPException
from pytest import mark, raises

from models import UserPool
from utils.auth.token import decode_access_token, generate_access_token
from utils.test import local_client


@mark.asyncio
async def test_ping():
    async with local_client() as client:
        resp = await client.get('http://app.invalid/ping')

        assert resp.status_code == 200
        assert resp.json() == 'pong'


def test_access_token(userpool: UserPool):
    token = generate_access_token(userpool, userpool.applications[0])
    decoded = decode_access_token(token)
    assert type(decoded) is dict

    with raises(HTTPException):
        decode_access_token('test')

    with raises(HTTPException):
        decode_access_token(generate_access_token(userpool, userpool.applications[0], timedelta(seconds=-60)))
