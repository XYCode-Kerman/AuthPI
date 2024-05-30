import random

from bson import ObjectId
from faker import Faker
from pytest import mark

from models import User, UserPool
from utils.test import local_client

faker = Faker(locale='zh-CN')

# 创建测试用户
TEST_USER = User(
    username=faker.user_name(),
    password=faker.password(),
    name=faker.name(),
    nickname=faker.name(),
    externalId="test",
    status="Activated",
    gender=random.choice(['Male', 'Female']),
    geography_datas={
        "country": faker.country(),
        "province": faker.province(),
        "city": faker.city_name(),
        "address": faker.address(),
        "streetAddress": faker.address(),
        "postalCode": faker.postcode()
    },
    privacy_datas={
        "company": faker.company(),
        "browser": faker.user_agent(),
        "device": random.choice(['Phone', 'PC', 'Laptop']),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "phoneCountryCode": str(faker.phonenumber_prefix())
    },
    emailVerified=False,
    phoneVerified=False,
    avatar=faker.image_url()
)


@mark.asyncio
async def test_user_operations(userpool: UserPool, application_access_token: str):
    async with local_client() as client:
        # 获取
        resp = await client.get('/management/user/', headers={
            'X-Application-Access-Token': application_access_token
        })

        assert resp.status_code == 200
        assert type(resp.json()) == list

        # 增加
        resp = await client.post('/management/user/', headers={
            'X-Application-Access-Token': application_access_token
        }, json=TEST_USER.model_dump(mode='json'))

        assert resp.status_code == 200
        assert resp.json()['username'] == TEST_USER.username

        # 增加已存在
        resp = await client.post('/management/user/', headers={
            'X-Application-Access-Token': application_access_token
        }, json=TEST_USER.model_dump(mode='json'))

        assert resp.status_code == 400
        assert resp.json() == {'detail': '用户已存在'}

        # 更新
        TEST_USER_UPDATED = TEST_USER.model_copy()
        TEST_USER_UPDATED.name = faker.name()
        resp = await client.put(f'/management/user/{TEST_USER_UPDATED.id}', headers={
            'X-Application-Access-Token': application_access_token
        }, json=TEST_USER_UPDATED.model_dump(mode='json'))
        assert resp.status_code == 200
        assert resp.json()['name'] == TEST_USER_UPDATED.name

        # 获取详情
        resp = await client.get(f'/management/user/{TEST_USER_UPDATED.id}', headers={
            'X-Application-Access-Token': application_access_token
        })
        assert resp.status_code == 200
        assert resp.json()['username'] == TEST_USER_UPDATED.username
        assert resp.json()['name'] == TEST_USER_UPDATED.name

        # 获取、更新不存在
        resp = await client.get(f'/management/user/{ObjectId()}', headers={
            'X-Application-Access-Token': application_access_token
        })
        assert resp.status_code == 404
        assert resp.json() == {'detail': '用户不存在'}

        resp = await client.put(f'/management/user/{ObjectId()}', headers={
            'X-Application-Access-Token': application_access_token
        }, json=TEST_USER_UPDATED.model_dump(mode='json'))
        assert resp.status_code == 404
        assert resp.json() == {'detail': '用户不存在'}

        # 删除
        resp = await client.delete(f'/management/user/{TEST_USER_UPDATED.id}', headers={
            'X-Application-Access-Token': application_access_token
        })
        assert resp.status_code == 200

        # 删除不存在
        resp = await client.delete(f'/management/user/{TEST_USER_UPDATED.id}', headers={
            'X-Application-Access-Token': application_access_token
        })
        assert resp.status_code == 404
