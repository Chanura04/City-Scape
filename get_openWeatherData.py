import requests
import os
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
# city = "Milan"
GEODB_KEY=os.environ.get("GEO_DB_KEY")
OPENWEATHER_KEY=os.getenv("OPENWEATHER")
# geo_url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
# geo_headers = {"X-RapidAPI-Key": GEODB_KEY, "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"}
# geo_params = {"namePrefix": city}
# geo_res = requests.get(geo_url, headers=geo_headers, params=geo_params).json()
#
# # if not geo_res["data"]:
# #     return f"City '{city}' not found", 404
#
# city_info = geo_res["data"][0]
# lat, lon = city_info["latitude"], city_info["longitude"]
#
# # 2) Get Weather (OpenWeather)
# weather_url = f"https://api.openweathermap.org/data/2.5/weather"
# weather_params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric"}
# weather_res = requests.get(weather_url, params=weather_params).json()
# city = weather_res["name"]
# country = weather_res["sys"]["country"]
# temperature = weather_res["main"]["temp"]
# feels_like = weather_res["main"]["feels_like"]
# condition = weather_res["weather"][0]["description"]
# humidity = weather_res["main"]["humidity"]
# pressure = weather_res["main"]["pressure"]
# wind_speed = weather_res["wind"]["speed"]
# clouds = weather_res["clouds"]["all"]
#
# # Convert sunrise/sunset from UNIX timestamp
# sunrise = datetime.fromtimestamp(weather_res["sys"]["sunrise"])
# sunset = datetime.fromtimestamp(weather_res["sys"]["sunset"])




















owm = OWM("a329977304afdfe0aa41109b14242310")
mgr = owm.weather_manager()


# Search for current weather in London (Great Britain) and get details
observation = mgr.weather_at_place('deefefwefw')
w = observation.weather
print(f"weather: {w}")

reference_time=w.reference_time(timeformat='iso')   #Time of the weather observation
detailed_status=w.detailed_status         # 'clouds'   Condition
general_status=w.status
# wind=w.wind()                  # {'speed': 4.6, 'deg': 330}
wind_direction=w.wind()['deg']
wind_speed=w.wind()['speed']
humidity=w.humidity                # 87
temperature=w.temperature('celsius')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
rain=w.rain                    # {}  rain volume
heat_index=w.heat_index              # None
clouds=w.clouds                  # 75  Cloud coverage percentage
pressure=w.pressure#Atmospheric pressure in hPa
snow=w.snow#Dictionary with snow volume
visibility_distance=w.visibility_distance   #Visibility in meters
sunrise_time=w.sunrise_time(timeformat='iso')
sunset_time=w.sunset_time(timeformat='iso')








print("----")
print(detailed_status)
print("----")
print(wind_direction)
print("----")
print(wind_speed)
print("----")
print(humidity)
print("----")
print(temperature)
print("----")
print(rain)
print("----")
print(heat_index)
print("----")
print(clouds)
print("----")
print(reference_time)