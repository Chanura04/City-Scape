from sqlalchemy import Column, Integer, String, DateTime,ForeignKey



from .base import Base
class ImageData(Base):
    __tablename__ = 'image_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String,ForeignKey('userdata.unique_id'), nullable=False)
    email = Column(String(50),ForeignKey('userdata.email'), nullable=False)
    image_url = Column(String(250))
    image_name = Column(String(250))
    updated_time = Column(DateTime, nullable=False)
    query_status= Column(String(250), nullable=False)