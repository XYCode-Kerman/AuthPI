
import random

from bson import ObjectId
from faker import Faker
from pytest import mark

from config import SUPER_USER_TOKEN
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

pytestmark = mark.asyncio


async def test_get_userpools():
    async with local_client() as client:
        resp = await client.get('http://app.invalid/management/userpool/')

        assert resp.status_code == 403
        assert resp.json() == {'detail': 'Not authenticated'}

        resp = await client.get('http://app.invalid/management/userpool/', headers={
            'su-token': SUPER_USER_TOKEN
        })

        assert resp.status_code == 200
        assert type(resp.json()) == list


async def test_create_delete_put_get_detail_userpool():
    """测试创建、删除、修改、获取用户池详情"""
    async with local_client() as client:
        # 新增
        resp = await client.post('http://app.invalid/management/userpool/', headers={
            'su-token': SUPER_USER_TOKEN
        }, json=TEST_USERPOOL)

        assert resp.status_code == 200
        assert resp.json()['name'] == TEST_USERPOOL['name']

        # 获取详情
        resp = await client.get(f'http://app.invalid/management/userpool/{TEST_USERPOOL["id"]}', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 200
        assert resp.json()['name'] == TEST_USERPOOL['name']

        # 修改
        TEST_USERPOOL2 = TEST_USERPOOL.copy()
        TEST_USERPOOL2['description'] = 'test'
        resp = await client.put(f'http://app.invalid/management/userpool/{TEST_USERPOOL["id"]}', headers={
            'su-token': SUPER_USER_TOKEN
        }, json=TEST_USERPOOL2)
        assert resp.status_code == 200

        # 修改不存在用户池
        TEST_USERPOOL2 = TEST_USERPOOL.copy()
        TEST_USERPOOL2['description'] = 'test'
        resp = await client.put(f'http://app.invalid/management/userpool/{ObjectId()}', headers={
            'su-token': SUPER_USER_TOKEN
        }, json=TEST_USERPOOL2)
        assert resp.status_code == 404
        assert resp.json() == {"detail": "用户池不存在"}

        # 再次获取详情
        resp = await client.get(f'http://app.invalid/management/userpool/{TEST_USERPOOL["id"]}', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 200
        assert resp.json()['description'] == TEST_USERPOOL2['description']

        # 删除存在
        resp = await client.delete(f'http://app.invalid/management/userpool/{TEST_USERPOOL["id"]}', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 200
        assert resp.json() is True

        # 删除不存在
        resp = await client.delete(f'http://app.invalid/management/userpool/{ObjectId()}', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 404
        assert resp.json() == {"detail": "用户池不存在"}

        # 获取不存在
        resp = await client.get(f'http://app.invalid/management/userpool/{ObjectId()}', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 404
        assert resp.json() == {"detail": "用户池不存在"}
