from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from .models import store_event_data,user_data_model ,store_log_data,store_weather_data,store_image_data,store_near_cities_model
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import session
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def store_user_data(first_name, last_name, email, password,fernet_key,account_created_on,signup_status,account_status, role):
    session = SessionLocal()
    try:
        user_data = user_data_model.UserData(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            unique_id=fernet_key,
            account_created_on=account_created_on,
            signup_status=signup_status,
            account_status=account_status,
            role=role
        )
        print(user_data)
        print(user_data.role)
        print(user_data.email)
        print(user_data.password)
        print(user_data.first_name)
        print(user_data.last_name)
        print(user_data.account_created_on)
        print(user_data.account_updated_on)

        session.add(user_data)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False

def check_user_exists(email):
    session = SessionLocal()
    try:
        user_data = session.query(user_data_model.UserData).filter(user_data_model.UserData.email == email).first()
        if user_data:
            return True
        else:
            return False

    except Exception as e:
        print(e)

def get_current_user_unique_id(email):
    session = SessionLocal()
    try:
        user_data = session.query(user_data_model.UserData).filter(user_data_model.UserData.email == email).first()
        if user_data:
            return user_data.unique_id
        else:
            return False
    except Exception as e:
        print(e)

def get_user_password(email):
    session = SessionLocal()
    try:
        user_data = session.query(user_data_model.UserData).filter(user_data_model.UserData.email == email).first()
        if user_data:
            return user_data.password
        else:
            return False
    except Exception as e:
        print(e)

def get_user_role(email):
    session = SessionLocal()
    try:
        user_data = session.query(user_data_model.UserData).filter(user_data_model.UserData.email == email).first()
        if user_data:
            return user_data.role
        else:
            return False
    except Exception as e:
        print(e)

def get_user_first_name(email):
    session = SessionLocal()
    try:
        user_data = session.query(user_data_model.UserData).filter(user_data_model.UserData.email == email).first()
        if user_data:
            return user_data.first_name
        else:
            return False
    except Exception as e:
        print(e)

def update_accountUpdatedOn_column(email):
    session = SessionLocal()
    try:
        user_data = session.query(user_data_model.UserData).filter(user_data_model.UserData.email == email).first()
        if user_data:
            sri_lanka_tz = ZoneInfo("Asia/Colombo")
            local_time = datetime.now(sri_lanka_tz)
            user_data.account_updated_on =local_time
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        print(e)















#Election Template Data

def store_log_data_db(
                unique_id,
                city_or_country,
                email,
                local_time,
                query_status
    ):
    session=SessionLocal()
    try:

        log_data= store_log_data.LogData(
            unique_id=unique_id,
            city_or_country=city_or_country,
            email=email,

            updated_time=local_time,
                query_status=query_status
        )
        session.add(log_data)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False

def get_country_or_city_input(log_data_unique_id):
    session = SessionLocal()
    try:
        log_data = session.query(store_log_data.LogData).filter(store_log_data.LogData.unique_id == log_data_unique_id).first()
        if log_data:
            return log_data.city_or_country
        else:
            return False
    except Exception as e:
        print(e)


def get_current_query_data(log_data_unique_id):
    session = SessionLocal()
    try:
        log_data = session.query(store_log_data.LogData).filter(store_log_data.LogData.unique_id == log_data_unique_id).first()
        if log_data:
            return [log_data.unique_id,log_data.city_or_country, log_data.email]
        else:
            return False
    except Exception as e:
        print(e)




def store_weather_data_db(
        unique_id,
        email,
        reference_time,
        details_about,
        detailed_status,
        general_status,
        wind_direction,
        wind_speed,
        humidity,
        temp_max,
        temp_min,
        temp_normal,

        heat_index,
        clouds,
        pressure,

        visibility_distance,
        sunrise_time,
        sunset_time,
        updated_time,
        query_status
    ):
    session=SessionLocal()
    try:
        weather_data= store_weather_data.WeatherData(
            unique_id=unique_id,
            email=email,
            reference_time=reference_time,
            details_about=details_about,

            detailed_status=detailed_status,
            general_status=general_status,
            wind_direction=wind_direction,
            wind_speed=wind_speed,
            humidity=humidity,
            temp_max=temp_max,
            temp_min=temp_min,
            temp_normal=temp_normal,

            heat_index=heat_index,
            clouds=clouds,
            pressure=pressure,

            visibility_distance=visibility_distance,
            sunrise_time=sunrise_time,
            sunset_time=sunset_time,
            updated_time=updated_time,
            query_status=query_status
        )
        session.add(weather_data)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False

def get_weather_data(unique_id):
    session = SessionLocal()
    try:
        weather_data = session.query(store_weather_data.WeatherData).filter(store_weather_data.WeatherData.unique_id == unique_id).first()
        if weather_data:
            return [
                weather_data.reference_time,
                weather_data.detailed_status,
                weather_data.general_status,
                weather_data.wind_direction,
                weather_data.wind_speed,
                weather_data.humidity,
                weather_data.temp_max,
                weather_data.temp_min,
                weather_data.temp_normal,
                weather_data.heat_index,
                weather_data.clouds,
                weather_data.pressure,
                weather_data.visibility_distance,
                weather_data.sunrise_time,
                weather_data.sunset_time
            ]
        else:
            return False
    except Exception as e:
        print(e)




#
# Photo url:  https://images.pexels.com/photos/1619854/pexels-photo-1619854.jpeg
# Photo name:  Stunning aerial view capturing Sydney Opera House and Harbour Bridge in daylight.
# Photo url:  https://images.pexels.com/photos/995765/pexels-photo-995765.jpeg
# Photo name:  A stunning view of the Sydney Opera House and harbor illuminated at twilight, showcasing city life and architecture.
# Photo url:  https://images.pexels.com/photos/1878293/pexels-photo-1878293.jpeg
# Photo name:  Beautiful view of the Sydney Opera House and its reflection at dusk, highlighting iconic architecture.
# Photo url:  https://images.pexels.com/photos/783682/pexels-photo-783682.jpeg
# Photo name:  Stunning view of Sydney's skyline featuring the Harbour Bridge and Opera House under a clear blue sky.
# Photo url:  https://images.pexels.com/photos/995764/pexels-photo-995764.jpeg
# Photo name:  Captivating view of Sydney's illuminated skyline with the iconic Opera House and harbor at night.

def add_image_data(unique_id,email,image_url,image_name, updated_time,status):
    session=SessionLocal()
    try:
        image_data= store_image_data.ImageData(
            unique_id=unique_id,
            image_url=image_url,
            image_name=image_name,
            email=email,
            updated_time=updated_time,
            query_status=status
        )
        session.add(image_data)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_image_data(unique_id):
    session = SessionLocal()
    try:
        image_data = session.query(store_image_data.ImageData).filter(store_image_data.ImageData.unique_id == unique_id).first()
        if image_data:
            return [image_data.image_url,image_data.image_name]
        else:
            return False
    except Exception as e:
        print(e)

def add_near_city_data_db(unique_id,email,user_input,city_name,distance,updated_time,status):
    session=SessionLocal()
    try:
        city_data= store_near_cities_model.CityData(
            unique_id=unique_id,
            details_about=user_input,
            city_name=city_name,
            distance=distance,
            email=email,
            updated_time=updated_time,
            query_status=status
        )
        session.add(city_data)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False

def get_near_cities_data(unique_id):
    session = SessionLocal()
    try:
        city_data = session.query(store_near_cities_model.CityData).filter(store_near_cities_model.CityData.unique_id == unique_id).first()
        if city_data:
            return [city_data.details_about,city_data.city_name,city_data.distance]
        else:
            return False
    except Exception as e:
            print(e)







def store_event_data_db(unique_id,email,event_name,event_date,event_time,event_location,img_url,updated_time,status):
    session=SessionLocal()
    try:
        event_data= store_event_data.EventData(
            unique_id=unique_id,
            event_name=event_name,
            event_date=event_date,
            event_time=event_time,
            email=email,
            event_location=event_location,
            image_url=img_url,
            query_status=status,
            updated_time=updated_time


        )
        session.add(event_data)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False

def get_event_data(unique_id):
    session = SessionLocal()
    try:
        event_data = session.query(store_event_data.EventData).filter(store_event_data.EventData.unique_id == unique_id).first()
        if event_data:
            return [event_data.event_name,event_data.event_date,event_data.event_time,event_data.event_location,event_data.image_url]
        else:
            return False
    except Exception as e:
            print(e)