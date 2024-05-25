from datetime import date
from typing import Literal, Optional

from odmantic import Model
from pydantic import BaseModel

UserStatus = Literal['Suspended', 'Resigned', 'Activated', 'Archived', 'Deactivated']
UserGender = Literal['Male', 'Female', 'Undefined']


class UserGeographyData(BaseModel):
    country: Optional[str]
    province: Optional[str]
    city: Optional[str]
    address: Optional[str]
    streetAddress: Optional[str]
    postalCode: Optional[str]


class UserPrivacyData(BaseModel):
    company: Optional[str]
    browser: Optional[str]
    device: Optional[str]
    birthdate: Optional[date]
    email: Optional[str]
    phone: Optional[str]
    phoneCountryCode: Optional[str]


class User(Model):
    username: str
    password: str
    name: str
    nickname: str
    externalId: str
    status: UserStatus
    gender: UserGender
    geography_datas: UserGeographyData
    privacy_datas: UserPrivacyData
    emailVerified: bool = False
    phoneVerified: bool = False
    avatar: Optional[str]
