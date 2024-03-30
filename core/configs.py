#configura as varíaveis de sessão com o banco de dados
from pydantic.v1 import BaseSettings
from sqlalchemy.ext.declarative import declarative_base
import os 

class Settings(BaseSettings):
    DATABASE_URL = os.getenv('DATABASE_URL') 
    API_V = os.getenv('API_V')
    DB_BaseModel = declarative_base()
    
    JWT_SECRET = os.getenv('SECRET')
    ALGORITHM = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    
    class Config:
        sensitive_case = True

settings = Settings()
        
        
