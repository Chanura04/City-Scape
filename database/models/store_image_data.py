from sqlalchemy import Column, Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ImageData(Base):
    __tablename__ = 'image_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    image_name = Column(String, nullable=False)
    updated_time = Column(DateTime, nullable=False)
    query_status= Column(String, nullable=False)