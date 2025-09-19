from sqlalchemy import Column, Integer, String, DateTime,ForeignKey



from .base import Base
class CityData(Base):
    __tablename__ = 'near_city_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String,ForeignKey('userdata.unique_id') ,nullable=False)
    email = Column(String(50),ForeignKey('userdata.email') , nullable=False)
    details_about= Column(String(20), nullable=False)
    city_name = Column(String(20))
    distance = Column(String(20))
    updated_time = Column(DateTime, nullable=False)
    query_status= Column(String(250), nullable=False)