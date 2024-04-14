from fastapi import APIRouter
from api.v1.endpoints import users
from api.v1.endpoints import roles

router = APIRouter()

router.include_router(router=users.router,prefix='/users',tags=['users'])
router.include_router(router=roles.router,prefix='/roles',tags=['roles'])
