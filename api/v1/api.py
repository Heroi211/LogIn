from fastapi import APIRouter
from api.v1.endpoints import users
from api.v1.endpoints import roles
from api.v1.endpoints import routines
from api.v1.endpoints import clients

router = APIRouter()
router.include_router(router=users.router,prefix='/users',tags=['users'])
router.include_router(router=roles.router,prefix='/roles',tags=['roles'])
router.include_router(router=routines.router,prefix='/routines',tags=['routines'])
router.include_router(router=clients.router,prefix='/clients',tags=['clients'])

