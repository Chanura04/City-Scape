from sqlalchemy import Column, Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CityData(Base):
    __tablename__ = 'near_city_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    details_about= Column(String, nullable=False)
    city_name = Column(String)
    distance = Column(Integer)
    updated_time = Column(DateTime, nullable=False)
    query_status= Column(String, nullable=False)