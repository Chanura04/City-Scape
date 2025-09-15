from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LogData(Base):
    __tablename__ = 'log_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    city_or_country = Column(String, nullable=False)


    updated_time = Column(DateTime, nullable=False)

    query_status= Column(String, nullable=False)





