from fastapi.security import OAuth2PasswordBearer

from core.configs import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.PROJECT_VERSION}/users/login")
