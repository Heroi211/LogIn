from fastapi import APIRouter

from contexts.identity_access.presentation.api.v1.endpoints import permissions, roles, users

router = APIRouter()
router.include_router(router=users.router, prefix="/users", tags=["users"])
router.include_router(router=roles.router, prefix="/roles", tags=["roles"])
router.include_router(router=permissions.router, prefix="/permissions", tags=["permissions"])
