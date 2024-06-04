from fastapi import APIRouter

from . import oidc

router = APIRouter(prefix='/auth', tags=['验证'])
router.include_router(oidc.router)

__all__ = ['router']
