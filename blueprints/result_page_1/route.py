import uuid
from .api_details_pexels import API
import folium
import requests
from flask import Blueprint, render_template, session, request, redirect, url_for
import os
from dotenv import load_dotenv
load_dotenv()
from pyowm import OWM
import time
import http.client
import json
import urllib.parse
from helpers import current_local_time
from database.database import get_image_data,add_image_data, get_country_or_city_input,get_current_query_data,store_log_data_db,store_weather_data_db
result_page_1_bp=Blueprint('result_page_1', __name__, template_folder='templates', static_folder='static')








def get_map_data():
    country_or_city_input = get_country_or_city_input(session.get('log_data_unique_id'))
    encoded_input = urllib.parse.quote(country_or_city_input)
    GEODB_KEY = os.getenv("GEO_DB_KEY")

    headers = {
        'x-rapidapi-key': GEODB_KEY,
        'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
    }
    conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

    # 1) Always search in cities endpoint
    conn.request("GET", f"/v1/geo/cities?namePrefix={encoded_input}", headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))

    if "data" not in data or not data["data"]:
        print("No results found for country or city")
        return f"No results found for {country_or_city_input}"

    first = data["data"][0]
    wikiDataId = first.get("wikiDataId")
    country_code = first.get("countryCode")
    city_name = first.get("city")
    lat = first.get("latitude")
    lon = first.get("longitude")
    print(f"lat: {lat}, lon: {lon}")

    # 2) Wait a bit (avoid BASIC plan rate limit)
    time.sleep(1)

    # 3) Get local time for that city
    conn.request("GET", f"/v1/geo/cities/{wikiDataId}/dateTime", headers=headers)
    res = conn.getresponse()
    time_data = json.loads(res.read().decode("utf-8"))

    country_date = time_data.get("data").split("T")[0]
    country_time = time_data.get("data").split("T")[1].split("+")[0]

    TRANSITLAND_API_KEY=os.getenv("TRANSITLAND_API_KEY")

    transit_url = "https://transit.land/api/v2/rest/stops"
    transit_params = {"lat": lat, "lon": lon, "r": 5000, "limit": 5}  # 5km radius
    transit_res = requests.get(transit_url, params=transit_params).json()


    fmap = folium.Map(location=[lat, lon], zoom_start=12)
    # folium.Marker([lat, lon], popup=f"📍 {city_info['city']}").add_to(fmap)
    folium.Marker([lat, lon], popup=f"📍 {country_or_city_input}").add_to(fmap)

    if "stops" in transit_res:
        for stop in transit_res["stops"]:
            folium.CircleMarker(
                [stop["lat"], stop["lon"]],
                radius=5, color="blue",
                popup=f"🚉 {stop['name']}"
            ).add_to(fmap)

    map_html = fmap._repr_html_()
    return [map_html,country_date,country_time,country_code]

@result_page_1_bp.route("/data" )
def show_page_one_data():

        if session.get('email'):
            try:
                country_or_city_input = get_country_or_city_input(session.get('log_data_unique_id'))
                print(f"country_or_city_input: {country_or_city_input}")

                OPENWEATHER_KEY = os.getenv("OPENWEATHER")

                owm = OWM(OPENWEATHER_KEY)
                mgr = owm.weather_manager()

                # Search for current weather in London (Great Britain) and get details
                observation = mgr.weather_at_place(country_or_city_input)
                w = observation.weather

                reference_time = w.reference_time(timeformat='iso')  # Time of the weather observation
                detailed_status = w.detailed_status  # 'clouds'   Condition
                general_status = w.status
                # wind=w.wind()                  # {'speed': 4.6, 'deg': 330}
                wind_direction = w.wind()['deg']
                wind_speed = w.wind()['speed']
                humidity = w.humidity  # 87
                temperature = w.temperature('celsius')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
                temp_max=temperature['temp_max']
                temp_min=temperature['temp_min']
                temp_normal=temperature['temp']


                heat_index = w.heat_index  # None
                clouds = w.clouds  # 75  Cloud coverage percentage
                pressure = w.pressure['press']  # Atmospheric pressure in hPa

                visibility_distance = w.visibility_distance  # Visibility in meters
                sunrise_time = w.sunrise_time(timeformat='iso')
                sunset_time = w.sunset_time(timeformat='iso')
                unique_id = str(uuid.uuid4())

                session['weather_data_unique_id'] = unique_id

                store_weather_data_db(
                    email=session.get('email'),
                    unique_id=session.get('log_data_unique_id'),
                    reference_time=reference_time,
                    details_about=country_or_city_input,
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
                    updated_time=current_local_time(),
                    query_status="success")


                print(f""" 
                    reference_time: {reference_time}\n
                    detailed_status: {detailed_status}\n
                    general_status: {general_status}\n
                    wind_direction: {wind_direction}\n
                    wind_speed: {wind_speed}\n
                    humidity: {humidity}\n
                    temperature: {temperature}\n    
                    heat_index: {heat_index}\n
                    clouds: {clouds}\n
                    pressure: {pressure}\n
                    visibility_distance: {visibility_distance}\n
                    sunrise_time: {sunrise_time}\n
                    sunset_time: {sunset_time}\n
                        """)

                local_time = current_local_time()
                stored_data = get_current_query_data(session.get('log_data_unique_id'))
                if stored_data:
                    store_log_data_db(
                        stored_data[0],
                        stored_data[1],
                        stored_data[2],
                        local_time,
                        "Openweather api fetch success")
                else:
                    print("No log data found for the given time.")

                get_map=get_map_data()
                imges=get_pexels_data()
                near_places=show_near_places()
                return render_template("result_main_page.html",
                                       reference_time=reference_time,
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
                                       user_input=country_or_city_input,
                                       map_html=get_map[0],
                                       date=get_map[1],
                                       time=get_map[2],
                                       country_code=get_map[3],

                                       first_img_name=imges[0]["img_name"],
                                       first_img_url=imges[0]["url"],
                                       second_img_name=imges[1]["img_name"],
                                       second_img_url=imges[1]["url"],
                                       third_img_name=imges[2]["img_name"],
                                       third_img_url=imges[2]["url"],
                                       fourth_img_name=imges[3]["img_name"],
                                       fourth_img_url=imges[3]["url"],
                                       fifth_img_name=imges[4]["img_name"],
                                       fifth_img_url=imges[4]["url"],

                                       near_place_one_city=near_places[0]["city"],
                                       near_place_one_distance=near_places[0]["distance"],
                                       near_place_two_city=near_places[1]["city"],
                                       near_place_two_distance=near_places[1]["distance"],
                                       near_place_three_city=near_places[2]["city"],
                                       near_place_three_distance=near_places[2]["distance"],
                                       nedar_place_four_city=near_places[3]["city"],
                                       nedar_place_four_distance=near_places[3]["distance"],
                                       nedar_place_five_city=near_places[4]["city"],
                                       nedar_place_five_distance=near_places[4]["distance"]



                                       )

            except Exception as e:

                local_time = current_local_time()
                stored_data=get_current_query_data(session.get('log_data_unique_id'))
                store_log_data_db(
                    stored_data[0],
                    stored_data[1],
                    stored_data[2],
                    local_time,e)
                print(e)


        else:
            return redirect(url_for("auth.login"))
        return  render_template("result_main_page.html")

def get_pexels_data():
    try:
        country_or_city_input = get_country_or_city_input(session.get('log_data_unique_id'))

        API_KEY = os.environ.get("PIXELS_API_KEY")
        api = API(API_KEY)

        # Initial search
        api.search(country_or_city_input, results_per_page=5)
        photos = api.get_entries()
        img_data=[]


        if photos:
            for photo in photos:
                img_data_dict = {
                    "img_name": "",
                    "url": ""
                }
                img_data_dict["img_name"]=photo.img_name()
                img_data_dict["url"]=photo.url()
                img_data.append(img_data_dict)

                add_image_data(
                    session.get('log_data_unique_id'),
                    session.get('email'),
                    photo.url(),
                    photo.img_name(),
                    current_local_time(),
                    'Pexels api fetch success')

                print("Photo url: ", photo.url())
                print("Photo name: ", photo.img_name())

            stored_data = get_current_query_data(session.get('log_data_unique_id'))
            if stored_data:
                local_time = current_local_time()
                store_log_data_db(
                    stored_data[0],
                    stored_data[1],
                    stored_data[2],
                    local_time,
                    "Pexels api fetch success")


        else:
            print("No photos found.")
        time.sleep(2)
        print("dict: ",img_data)
        return img_data
    except Exception as e:
        print(e)

        stored_image_data=get_image_data(session.get('log_data_unique_id'))

        if stored_image_data:
            add_image_data(
                session.get('log_data_unique_id'),
                session.get('email'),
                stored_image_data[0],
                stored_image_data[1],
                current_local_time(),
                e)

        stored_data = get_current_query_data(session.get('log_data_unique_id'))
        if stored_data:
            local_time = current_local_time()
            store_log_data_db(
                stored_data[0],
                stored_data[1],
                stored_data[2],
                local_time,
                e)

        return False

def show_near_places():
    conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "9b7c9d2e99msh91a2a51875d27bcp19318ejsn6e1c032e0a1f",
        'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
    }

    conn.request("GET", "/v1/geo/cities/Q60/nearbyCities?radius=100", headers=headers)

    res = conn.getresponse()

    data = json.loads(res.read().decode("utf-8"))
    list = []
    dict_location = data['data']
    for i in dict_location:
        dict = {
            "city": i.get("city"),
            "distance": i.get("distance")
        }
        list.append(dict)

    print("\n\nNear Places: ", list)
    print("Near Places Length: ", len(list))
    return list