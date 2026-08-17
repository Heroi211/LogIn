from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import api
from api.v1.middleware import ValidateRequestBodyMiddleware
from core.configs import settings
from core.logging_api_request import setup_api_request_logging
from core.logging_setup import setup_root_logging
from core.middleware.request_record import request_record

setup_root_logging()
setup_api_request_logging()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
app.middleware("http")(request_record)
app.add_middleware(ValidateRequestBodyMiddleware)
app.include_router(api.router, prefix=settings.PROJECT_VERSION)

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

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
