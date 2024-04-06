from fastapi import FastAPI
from core.configs import settings
from api.v1 import api

app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
app.include_router(api.router,prefix=settings.PROJECT_VERSION)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)