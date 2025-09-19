from sqlalchemy import Column, String, Integer, DateTime, Boolean

from .base import Base
class UserData(Base):
    __tablename__ = 'userdata'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False,unique=True)
    password = Column(String(20), nullable=False)
    unique_id = Column(String(100), nullable=False,unique=True)

    account_created_on = Column(DateTime, nullable=False)
    account_updated_on = Column(DateTime, nullable=False)

    role = Column(String(20), nullable=False,default="user")

    signup_status = Column(Boolean, nullable=False)
    account_status = Column(Boolean, nullable=False)

