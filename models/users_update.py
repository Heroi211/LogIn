from core.configs import settings
from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import relationship
import datetime

class Users_update(settings.DB_BaseModel):
    __tablename__=('users_update')
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_changed = Column(Integer,ForeignKey='users.id')
    user_changer = Column(Integer,ForeignKey='users.id')
    updated_at = Column(DateTime,default=datetime.datetime.now(),nullable=False)
    name_changed = Column(String, nullable=True)
    email_changed = Column(String, nullable=True)
    password_changed = Column(String, nullable=True)
    active_changed = Column(String, nullable=True)
    role_changed = Column(Integer,nullable=True)
    
    relationship('Users', back_populates='users',lazy='joined')
    
    
    
    