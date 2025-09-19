from sqlalchemy import Column, String, Integer, DateTime, ForeignKey


from .base import Base
class LogData(Base):
    __tablename__ = 'log_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String, nullable=False)
    email = Column(String(50),ForeignKey('userdata.email') ,nullable=False)
    city_or_country = Column(String(20), nullable=False)


    updated_time = Column(DateTime, nullable=False)

    query_status= Column(String(250), nullable=False)





