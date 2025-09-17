from sqlalchemy import Column, Integer, String, DateTime, ForeignKey



from .base import Base
class EventData(Base):
    __tablename__ = 'event_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String, ForeignKey('userdata.unique_id'),nullable=False)
    email = Column(String,ForeignKey('userdata.email'), nullable=False)
    event_name = Column(String)
    event_date = Column(String)
    event_time = Column(String)
    event_location = Column(String)
    image_url = Column(String)
    updated_time = Column(DateTime, nullable=False)
    query_status= Column(String, nullable=False)