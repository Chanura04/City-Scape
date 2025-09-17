from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from .base import Base
class LogData(Base):
    __tablename__ = 'log_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String, nullable=False)
    email = Column(String,ForeignKey('userdata.email') ,nullable=False)
    city_or_country = Column(String, nullable=False)


    updated_time = Column(DateTime, nullable=False)

    query_status= Column(String, nullable=False)





