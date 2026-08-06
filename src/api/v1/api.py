from fastapi import APIRouter

from api.v1.endpoints import api_keys, auth, messaging, meta, roles, users

router = APIRouter()
router.include_router(router=meta.router, tags=["meta"])
router.include_router(router=auth.router, prefix="/auth", tags=["auth"])
router.include_router(router=messaging.router, prefix="/messaging", tags=["messaging"])
router.include_router(router=api_keys.router, prefix="/api-keys", tags=["api-keys"])
router.include_router(router=users.router, prefix="/users", tags=["users"])
router.include_router(router=roles.router, prefix="/roles", tags=["roles"])
