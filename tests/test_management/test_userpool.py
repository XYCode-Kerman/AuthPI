
from bson import ObjectId
from pytest import mark

from config import SUPER_USER_TOKEN
from utils.test import local_client

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
        resp = await client.get(f'http://app.invalid/management/userpool/{TEST_USERPOOL['id']}', headers={
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
        resp = await client.delete(f'http://app.invalid/management/userpool/{TEST_USERPOOL['id']}', headers={
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
