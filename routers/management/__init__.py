from fastapi import APIRouter

from . import userpool

router = APIRouter(tags=['管理'], prefix='/management')
router.include_router(userpool.router)


__all__ = ["router"]
