from fastapi.testclient import TestClient
from pytest import mark

from config import SUPER_USER_TOKEN

TEST_USERPOOL = {
    "name": "string",
    "description": "string",
    "users": [
        {
            "username": "string",
            "password": "string",
            "name": "string",
            "nickname": "string",
            "externalId": "string",
            "status": "Suspended",
            "gender": "Male",
            "geography_datas": {
                "country": "string",
                "province": "string",
                "city": "string",
                "address": "string",
                "streetAddress": "string",
                "postalCode": "string"
            },
            "privacy_datas": {
                "company": "string",
                "browser": "string",
                "device": "string",
                "email": "string",
                "phone": "string",
                "phoneCountryCode": "string"
            },
            "emailVerified": False,
            "phoneVerified": False,
            "avatar": "string",
            "id": "5f85f36d6dfecacc68428a46"
        }
    ],
    "applications": [
        {
            "name": "string",
            "slug": "string",
            "app_id": "string",
            "app_secret": "string",
            "auth_protocol": "OIDC",
            "id": "5f85f36d6dfecacc68428a46"
        }
    ],
    "resources": [
        {
            "slug": "string",
            "name": "string",
            "description": "string",
            "actions": [
                "string"
            ]
        }
    ],
    "id": "5f85f36d6dfecacc68428a46"
}

pytestmark = mark.asyncio


async def test_get_userpools(client):
    resp = client.get('/management/userpool/')

    assert resp.status_code == 403
    assert resp.json() == {'detail': 'Not authenticated'}

    resp = client.get('/management/userpool/', headers={
        'su-token': SUPER_USER_TOKEN
    })

    assert resp.status_code == 200
    assert type(resp.json()) == list


async def test_create_userpool():
    from main import app
    with TestClient(app) as client:
        resp = client.post('/management/userpool/', headers={
            'su-token': SUPER_USER_TOKEN
        }, json=TEST_USERPOOL)

        assert resp.status_code == 200
        assert resp.json()['name'] == TEST_USERPOOL['name']
