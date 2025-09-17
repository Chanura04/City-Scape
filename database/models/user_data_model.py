from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserData(Base):
    __tablename__ = 'userdata'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    fernet_key = Column(String, nullable=False,unique=True)

    account_created_on = Column(DateTime, nullable=False)
    account_updated_on = Column(DateTime, nullable=False)

    role = Column(String, nullable=False,default="user")

    signup_status = Column(Boolean, nullable=False)
    account_status = Column(Boolean, nullable=False)

