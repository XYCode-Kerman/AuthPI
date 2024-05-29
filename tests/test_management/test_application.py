from bson import ObjectId
from faker import Faker
from pytest import mark

from config import SUPER_USER_TOKEN
from models import UserPool
from utils.test import local_client

pytestmark = mark.asyncio


fake = Faker('zh_CN')


TEST_APPLICATION = {
    "name": fake.company(),
    "slug": fake.slug(),
    "app_id": fake.uuid4(),
    "app_secret": ''.join(fake.random_letters(length=128)),
    "auth_protocol": "OIDC",
    "id": str(ObjectId()),
}


async def test_application(userpool: UserPool):
    async with local_client() as client:
        # 新增
        resp = await client.post(f'/management/application/{userpool.id}/', json=TEST_APPLICATION, headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 200
        assert resp.json()['id'] == TEST_APPLICATION['id']

        # 获取全部
        resp = await client.get(f'/management/application/{userpool.id}/', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 200
        assert [x for x in resp.json() if x['id'] == TEST_APPLICATION['id']].__len__() == 1

        # 获取密钥
        resp = await client.get(f'/management/application/{userpool.id}/{TEST_APPLICATION["id"]}/access-token', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 200
        assert type(resp.json()) == str

        # 获取不存在应用密钥
        resp = await client.get(f'/management/application/{userpool.id}/{ObjectId()}/access-token', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 404
        assert resp.json() == {'detail': '应用不存在'}

        # 更新
        resp = await client.put(f'/management/application/{userpool.id}/{TEST_APPLICATION["id"]}', json={
            "name": "test_114514",
            "slug": "string",
            "app_id": "string",
            "app_secret": "string",
            "auth_protocol": "OIDC"
        }, headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 200
        assert resp.json()['name'] == 'test_114514'

        resp2 = await client.get(f'/management/application/{userpool.id}/', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp2.status_code == 200
        assert [x for x in resp2.json() if x['name'] == 'test_114514'].__len__() == 1

        # 删除存在
        resp = await client.delete(f'/management/application/{userpool.id}/{TEST_APPLICATION["id"]}', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 200
        assert resp.json() == {"detail": "应用已删除"}

        # 删除不存在
        resp = await client.delete(f'/management/application/{userpool.id}/{ObjectId()}', headers={
            'su-token': SUPER_USER_TOKEN
        })
        assert resp.status_code == 404
        assert resp.json() == {"detail": "应用不存在"}
