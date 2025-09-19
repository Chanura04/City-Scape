from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey


from .base import Base
class WeatherData(Base):
    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True)
    unique_id = Column(String,ForeignKey('userdata.unique_id'), nullable=False)
    email = Column(String(50),ForeignKey('userdata.email'), nullable=False)
    reference_time= Column(String(20) )
    details_about= Column(String(20) )
    detailed_status= Column(String(20) )
    general_status= Column(String(20) )
    wind_direction= Column(String(20) )
    wind_speed= Column(String(20) )
    humidity= Column(String(20) )


    temp_max= Column(String(20) )
    temp_min= Column(String(20) )
    temp_normal= Column(String(20) )


    heat_index= Column(String(20) )
    clouds= Column(String(20) )
    pressure= Column(String(20) )

    visibility_distance= Column(String(20)  )
    sunrise_time= Column(String(20) )
    sunset_time= Column(String(20) )




    updated_time = Column(DateTime )

    query_status= Column(String(250), nullable=False)

