from fastapi import APIRouter

from . import authentication

router = APIRouter(prefix='/oidc', tags=['OIDC'])
router.include_router(authentication.router)
