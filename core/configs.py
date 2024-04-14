#configura as varíaveis de sessão com o banco de dados
from pydantic.v1 import BaseSettings
from sqlalchemy.ext.declarative import declarative_base
import os

from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.')/'.env'

load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    PROJECT_NAME =  os.getenv('PROJECT_NAME')
    PROJECT_VERSION = os.getenv('PROJECT_VERSION')
    
    DATABASE_USER: str = os.getenv('DATABASE_USER')
    DATABASE_PASS: str = os.getenv('DATABASE_PASS')
    DATABASE_SERVER: str = os.getenv('DATABASE_SERVER')
    DATABASE_PORT: str = os.getenv('DATABASE_PORT')
    DATABASE_NAME: str = os.getenv('DATABASE_NAME')
    
    DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_NAME}" 
    DB_BaseModel = declarative_base()
    
    JWT_SECRET = os.getenv('SECRET')
    ALGORITHM = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    
    class Config:
        sensitive_case = True

settings:Settings = Settings()
        
        
        
