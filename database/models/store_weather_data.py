from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WeatherData(Base):
    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String,ForeignKey('log_data.unique_id'), nullable=False)
    email = Column(String,ForeignKey('userdata.email'), nullable=False)
    reference_time= Column(String )
    details_about= Column(String )
    detailed_status= Column(String )
    general_status= Column(String )
    wind_direction= Column(String )
    wind_speed= Column(String )
    humidity= Column(String )


    temp_max= Column(String )
    temp_min= Column(String )
    temp_normal= Column(String )


    heat_index= Column(String )
    clouds= Column(String )
    pressure= Column(String )

    visibility_distance= Column(String  )
    sunrise_time= Column(String )
    sunset_time= Column(String )




    updated_time = Column(DateTime )

    query_status= Column(String, nullable=False)

