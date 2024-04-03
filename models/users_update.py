from core.configs import settings
from sqlalchemy import Column,Integer,String,DateTime
from sqlalchemy.orm import relationship
import datetime

class Users_update(settings.DB_BaseModel):
    __tablename__=('users_update')
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_changed = Column(Integer)
    user_changer = Column(Integer)
    updated_at = Column(DateTime,default=datetime.datetime.now(),nullable=False)
    
    