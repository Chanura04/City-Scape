from sqlalchemy import Column, Integer, String, DateTime, ForeignKey



from .base import Base
class EventData(Base):
    __tablename__ = 'event_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String, ForeignKey('userdata.unique_id'),nullable=False)
    email = Column(String(50),ForeignKey('userdata.email'), nullable=False)
    event_name = Column(String(250))
    event_date = Column(String(50))
    event_time = Column(String(50))
    event_location = Column(String(250))
    image_url = Column(String(250))
    updated_time = Column(DateTime, nullable=False)
    query_status= Column(String(250), nullable=False)