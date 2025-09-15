import folium
import requests
from flask import session
import urllib.parse
import os
from dotenv import load_dotenv
load_dotenv()
import json
import time
import http.client
# --- Build Folium Map ---
#
# lat=42.46245
# lon=1.50209
# transit_url = "https://transit.land/api/v2/rest/stops"
# transit_params = {"lat": lat, "lon": lon, "r": 5000, "limit": 5}  # 5km radius
# transit_res = requests.get(transit_url, params=transit_params).json()
#
# city="Sri lanka"
# fmap = folium.Map(location=[lat, lon], zoom_start=12)
# # folium.Marker([lat, lon], popup=f"📍 {city_info['city']}").add_to(fmap)
# folium.Marker([lat, lon], popup=f"📍 {city}").add_to(fmap)
#
# if "stops" in transit_res:
#         for stop in transit_res["stops"]:
#             folium.CircleMarker(
#                 [stop["lat"], stop["lon"]],
#                 radius=5, color="blue",
#                 popup=f"🚉 {stop['name']}"
#             ).add_to(fmap)
#
#     # Save map to templates
# fmap.save("templates/map.html")

def get_map_data():
    country_or_city_input = "LK"
    encoded_input = urllib.parse.quote(country_or_city_input)
    GEODB_KEY = os.getenv("GEO_DB_KEY")

    headers = {
        'x-rapidapi-key': GEODB_KEY,
        'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
    }
    conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

    lat = None
    lon = None
    country_date = "N/A"
    country_time = "N/A"
    country_code = "N/A"
    city_name = country_or_city_input

    # First, try to search for a city
    conn.request("GET", f"/v1/geo/cities?namePrefix={encoded_input}", headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))

    if "data" in data and data["data"]:
        # City found, proceed with city-specific data
        first = data["data"][0]
        wikiDataId = first.get("wikiDataId")
        country_code = first.get("countryCode")
        city_name = first.get("city")
        lat = first.get("latitude")
        lon = first.get("longitude")

        # Get local time for that city
        time.sleep(1)
        conn.request("GET", f"/v1/geo/cities/{wikiDataId}/dateTime", headers=headers)
        res = conn.getresponse()
        time_data = json.loads(res.read().decode("utf-8"))
        country_date = time_data.get("data").split("T")[0]
        country_time = time_data.get("data").split("T")[1].split("+")[0]
    else:
        # No city found, try to search for a country
        conn.request("GET", f"/v1/geo/countries?namePrefix={encoded_input}", headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))

        if "data" in data and data["data"]:
            first = data["data"][0]
            country_code = first.get("code")
            lat = first.get("latitude")
            lon = first.get("longitude")
            city_name = first.get("name")  # Set to country name
        else:
            return "No results found for country or city"

    # If we have latitude and longitude, create the map
    if lat is not None and lon is not None:
        TRANSITLAND_API_KEY = os.getenv("TRANSITLAND_API_KEY")
        transit_url = "https://transit.land/api/v2/rest/stops"
        transit_params = {"lat": lat, "lon": lon, "r": 5000, "limit": 5}
        transit_res = requests.get(transit_url, params=transit_params).json()

        fmap = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], popup=f"📍 {city_name}").add_to(fmap)

        if "stops" in transit_res:
            for stop in transit_res["stops"]:
                folium.CircleMarker(
                    [stop["lat"], stop["lon"]],
                    radius=5, color="blue",
                    popup=f"🚉 {stop['name']}"
                ).add_to(fmap)

        map_html = fmap._repr_html_()
        return [map_html, country_date, country_time, country_code]

    return "Map could not be generated."
print(get_map_data())