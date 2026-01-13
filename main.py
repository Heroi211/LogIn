from fastapi import FastAPI
from core.configs import settings
from api.v1 import api
from api.v1.middleware import ValidateRequestBodyMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
app.add_middleware(ValidateRequestBodyMiddleware)
app.include_router(api.router,prefix=settings.PROJECT_VERSION)

# Configuração do CORS
origins = [
    "*",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)