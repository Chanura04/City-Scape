from sqlalchemy import Column, Integer, String, DateTime,ForeignKey

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CityData(Base):
    __tablename__ = 'near_city_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String,ForeignKey('log_data.unique_id') ,nullable=False)
    email = Column(String,ForeignKey('userdata.email') , nullable=False)
    details_about= Column(String, nullable=False)
    city_name = Column(String)
    distance = Column(String)
    updated_time = Column(DateTime, nullable=False)
    query_status= Column(String, nullable=False)