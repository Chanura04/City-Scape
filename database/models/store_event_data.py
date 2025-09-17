from sqlalchemy import Column, Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EventData(Base):
    __tablename__ = 'event_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    event_name = Column(String)
    event_date = Column(String)
    event_time = Column(String)
    event_location = Column(String)
    image_url = Column(String)
    updated_time = Column(DateTime, nullable=False)
    query_status= Column(String, nullable=False)