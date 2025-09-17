from sqlalchemy import Column, Integer, String, DateTime,ForeignKey

from sqlalchemy.ext.declarative import declarative_base

from .base import Base
class ImageData(Base):
    __tablename__ = 'image_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String,ForeignKey('userdata.unique_id'), nullable=False)
    email = Column(String,ForeignKey('userdata.email'), nullable=False)
    image_url = Column(String)
    image_name = Column(String)
    updated_time = Column(DateTime, nullable=False)
    query_status= Column(String, nullable=False)