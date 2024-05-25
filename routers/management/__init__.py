from fastapi import APIRouter

from . import application, userpool

router = APIRouter(tags=['管理'], prefix='/management')
router.include_router(userpool.router)
router.include_router(application.router)


__all__ = ["router"]
