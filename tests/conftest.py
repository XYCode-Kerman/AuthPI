import asyncio
import random

import pytest
import pytest_asyncio
from bson import ObjectId
from faker import Faker

from config import SUPER_USER_TOKEN
from models import UserPool
from utils.test import local_client

faker = Faker(locale='zh-CN')

TEST_USERPOOL = {
    "name": faker.word(),
    "description": ''.join(faker.random_letters(length=128)),
    "users": [
        {
            "username": faker.user_name(),
            "password": faker.password(),
            "name": faker.name(),
            "nickname": faker.name(),
            "externalId": "test",
            "status": "Suspended",
            "gender": random.choice(['Male', 'Female']),
            "geography_datas": {
                "country": faker.country(),
                "province": faker.province(),
                "city": faker.city_name(),
                "address": faker.address(),
                "streetAddress": faker.address(),
                "postalCode": faker.postcode()
            },
            "privacy_datas": {
                "company": faker.company(),
                "browser": faker.user_agent(),
                "device": random.choice(['Phone', 'PC', 'Laptop']),
                "email": faker.email(),
                "phone": faker.phone_number(),
                "phoneCountryCode": str(faker.phonenumber_prefix())
            },
            "emailVerified": False,
            "phoneVerified": False,
            "avatar": faker.image_url(),
            "id": ObjectId().__str__()
        }
    ],
    "applications": [
        {
            "name": ''.join(faker.random_letters(length=32)),
            "slug": ''.join(faker.random_letters(length=32)),
            "app_id": ''.join(faker.random_letters(length=32)),
            "app_secret": ''.join(faker.random_letters(length=32)),
            "auth_protocol": "OIDC",
            "id": ObjectId().__str__(),
        }
    ],
    "resources": [
        {
            "slug": faker.slug(),
            "name": faker.word(),
            "description": ''.join([faker.word() for _ in range(10)]),
            "actions": ['read', 'write']
        }
    ],
    "id": ObjectId().__str__()
}


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def userpool():
    async with local_client() as client:
        # 新增
        resp = await client.post('http://app.invalid/management/userpool/', headers={
            'su-token': SUPER_USER_TOKEN
        }, json=TEST_USERPOOL)

        assert resp.status_code == 200
        assert resp.json()['name'] == TEST_USERPOOL['name']
    return UserPool.model_validate(resp.json())


@pytest_asyncio.fixture(scope='session')
async def application_access_token(userpool: UserPool) -> str:
    async with local_client() as client:
        resp = await client.get(f'/management/application/{userpool.id}/{TEST_USERPOOL["applications"][0]["id"]}/access-token', headers={
            'su-token': SUPER_USER_TOKEN
        })

        assert resp.status_code == 200, resp.text
    return resp.json()
