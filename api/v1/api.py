from fastapi import APIRouter
from api.v1.endpoints import users

router = APIRouter()

router.include_router(router=users.router,prefix='/users',tags=['users'])
