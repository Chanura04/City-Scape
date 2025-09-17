import uuid

from .event_fetcher import EventsFetcher
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
import logging
from database.database import get_current_user_unique_id, get_event_data, store_event_data_db, get_image_data, add_image_data, \
    get_country_or_city_input, get_current_query_data, store_log_data_db, store_weather_data_db, add_near_city_data_db, \
    get_near_cities_data

result_page_1_bp = Blueprint('result_page_1', __name__, template_folder='templates', static_folder='static')


def get_map_data():
    """
    Fetches map data, location info, and transit stops for a given location (city or country)
    Returns: [map_html, country_date, country_time, country_code] or error message
    """
    try:
        unique_id=get_current_user_unique_id(session.get('email'))
        country_or_city_input = get_country_or_city_input(unique_id)

        if not country_or_city_input:
            logging.error("No country or city input found")
            return "No location input provided"

        encoded_input = urllib.parse.quote(country_or_city_input)
        GEODB_KEY = os.getenv("GEO_DB_KEY")

        if not GEODB_KEY:
            logging.error("GEO_DB_KEY not found in environment variables")
            return "Location service unavailable"

        headers = {
            'x-rapidapi-key': GEODB_KEY,
            'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
        }

        conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

        # 1) First try searching in cities endpoint
        location_data = None
        try:
            conn.request("GET", f"/v1/geo/cities?namePrefix={encoded_input}", headers=headers)
            res = conn.getresponse()

            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                if "data" in data and data["data"]:
                    location_data = data["data"][0]
                    location_data["type"] = "city"
                    print(f"Found as city: {location_data}")
        except Exception as e:
            logging.warning(f"Error searching cities: {e}")

        # 2) If no city found, try searching in countries endpoint
        if not location_data:
            try:
                time.sleep(1)  # Rate limiting
                conn.request("GET", f"/v1/geo/countries?namePrefix={encoded_input}", headers=headers)
                res = conn.getresponse()

                if res.status == 200:
                    data = json.loads(res.read().decode("utf-8"))
                    if "data" in data and data["data"]:
                        # For country, we need to get the capital city or use country center
                        country_info = data["data"][0]
                        country_code = country_info.get("code")

                        # Try to get capital city coordinates
                        time.sleep(1)  # Rate limiting
                        conn.request("GET",
                                     f"/v1/geo/countries/{country_code}/places?types=CITY&sort=-population&limit=1",
                                     headers=headers)
                        capital_res = conn.getresponse()

                        if capital_res.status == 200:
                            capital_data = json.loads(capital_res.read().decode("utf-8"))
                            if "data" in capital_data and capital_data["data"]:
                                capital_city = capital_data["data"][0]
                                location_data = {
                                    "wikiDataId": capital_city.get("wikiDataId"),
                                    "countryCode": country_code,
                                    "city": capital_city.get("name", country_info.get("name")),
                                    "latitude": capital_city.get("latitude"),
                                    "longitude": capital_city.get("longitude"),
                                    "type": "country_capital"
                                }
                                print(f"Found country capital: {location_data}")

                        # If capital not found, use country data if available
                        if not location_data and country_info.get("latitude") and country_info.get("longitude"):
                            location_data = {
                                "wikiDataId": country_info.get("wikiDataId"),
                                "countryCode": country_code,
                                "city": country_info.get("name"),
                                "latitude": country_info.get("latitude"),
                                "longitude": country_info.get("longitude"),
                                "type": "country"
                            }
                            print(f"Using country center: {location_data}")

            except Exception as e:
                logging.warning(f"Error searching countries: {e}")

        # 3) If still no location found, return error
        if not location_data:
            logging.warning(f"No results found for: {country_or_city_input}")
            return f"No results found for {country_or_city_input}"

        # Extract location data
        wikiDataId = location_data.get("wikiDataId")
        session['wikiDataId'] = wikiDataId
        country_code = location_data.get("countryCode")
        city_name = location_data.get("city")
        lat = location_data.get("latitude")
        lon = location_data.get("longitude")
        location_type = location_data.get("type", "unknown")

        if not all([lat, lon]):
            logging.error("Incomplete location data received")
            return "Invalid location data received"

        print(f"lat: {lat}, lon: {lon}, type: {location_type}")

        # 4) Get local time for that location
        country_date = "N/A"
        country_time = "N/A"

        if wikiDataId:
            try:
                time.sleep(1)  # Rate limiting
                conn.request("GET", f"/v1/geo/cities/{wikiDataId}/dateTime", headers=headers)
                res = conn.getresponse()

                if res.status == 200:
                    time_data = json.loads(res.read().decode("utf-8"))
                    if "data" in time_data and time_data["data"]:
                        country_date = time_data.get("data").split("T")[0]
                        country_time = time_data.get("data").split("T")[1].split("+")[0]
            except Exception as e:
                logging.warning(f"Error fetching datetime: {e}")

        # 5) Get transit data (only for cities, not countries)
        transit_stops = []
        if location_type in ["city", "country_capital"]:
            try:
                TRANSITLAND_API_KEY = os.getenv("TRANSITLAND_API_KEY")
                if TRANSITLAND_API_KEY:
                    transit_url = "https://transit.land/api/v2/rest/stops"
                    transit_params = {"lat": lat, "lon": lon, "r": 5000, "limit": 5}
                    transit_response = requests.get(transit_url, params=transit_params, timeout=10)
                    if transit_response.status_code == 200:
                        transit_res = transit_response.json()
                        if "stops" in transit_res:
                            transit_stops = transit_res["stops"]
            except Exception as e:
                logging.warning(f"Error fetching transit data: {e}")

        # 6) Create map with appropriate zoom level
        try:
            # Adjust zoom level based on location type
            if location_type == "country":
                zoom_level = 6  # Country level zoom
            elif location_type == "country_capital":
                zoom_level = 10  # Capital city zoom
            else:
                zoom_level = 12  # Regular city zoom

            fmap = folium.Map(location=[lat, lon], zoom_start=zoom_level)

            # Add appropriate marker based on location type
            if location_type == "country":
                marker_icon = "🏛️"
                popup_text = f"{marker_icon} {country_or_city_input} (Country)"
            elif location_type == "country_capital":
                marker_icon = "🏛️"
                popup_text = f"{marker_icon} {city_name} (Capital of {country_or_city_input})"
            else:
                marker_icon = "🏛️"
                popup_text = f"{marker_icon} {country_or_city_input}"

            folium.Marker([lat, lon], popup=popup_text).add_to(fmap)

            # Add transit stops if available (only for cities)
            for stop in transit_stops:
                try:
                    folium.CircleMarker(
                        [stop["lat"], stop["lon"]],
                        radius=5, color="blue",
                        popup=f"🚉 {stop['name']}"
                    ).add_to(fmap)
                except KeyError:
                    continue  # Skip malformed stop data

            map_html = fmap._repr_html_()
        except Exception as e:
            logging.error(f"Error creating map: {e}")
            return "Error creating map visualization"

        return [map_html, country_date, country_time, country_code]

    except Exception as e:
        logging.error(f"Unexpected error in get_map_data: {e}")
        return "Map service temporarily unavailable"


@result_page_1_bp.route("/data/<string:city_name>")
def show_page_one_data(city_name):
    """
    Main route handler for displaying weather and location data
    """
    # Check if user is logged in
    if not session.get('email'):
        return redirect(url_for("auth.login"))

    try:
        # Get user input
        # country_or_city_input = get_country_or_city_input(session.get('log_data_unique_id'))
        country_or_city_input=city_name

        if not country_or_city_input:
            logging.error("No country or city input found in session")
            return render_template("dashboard.html", error="Please enter a valid city name!")

        print(f"country_or_city_input: {country_or_city_input}")

        # Get weather data - THIS IS THE CRITICAL SECTION
        OPENWEATHER_KEY = os.getenv("OPENWEATHER")

        if not OPENWEATHER_KEY:
            logging.error("OpenWeather API key not found")
            return render_template("dashboard.html", error="Weather service unavailable!")

        try:
            owm = OWM(OPENWEATHER_KEY)
            mgr = owm.weather_manager()

            # This is where the error occurs for invalid locations
            observation = mgr.weather_at_place(country_or_city_input)
            w = observation.weather

            if not w:
                logging.error(f"No weather data received for: {country_or_city_input}")
                return render_template("dashboard.html", error="Please enter a valid city name!")

        except Exception as weather_api_error:
            # This catches the "Unable to find the resource" error
            logging.error(f"Weather API error for '{country_or_city_input}': {weather_api_error}")

            # Log the error in database
            try:
                local_time = current_local_time()
                unique_id=get_current_user_unique_id(session.get('email'))
                stored_data = get_current_query_data(unique_id)
                if stored_data:
                    store_log_data_db(
                        stored_data[0],
                        stored_data[1],
                        stored_data[2],
                        local_time,
                        f"Weather API failed: {str(weather_api_error)}")
            except Exception as log_error:
                logging.error(f"Error logging weather failure: {log_error}")

            # CRITICAL: Return dashboard with error - this should stop execution here
            # return render_template("dashboard.html", error="Please enter a valid city name!")
            return redirect(url_for("dashboard.dashboard"))
        # Extract weather data safely - only execute if weather fetch succeeded
        try:
            reference_time = w.reference_time(timeformat='iso')

            # Double check for valid data
            if not reference_time:
                logging.error(f"Invalid weather data for '{country_or_city_input}' - empty reference_time")
                return render_template("dashboard.html", error="Please enter a valid city name!")

            detailed_status = w.detailed_status
            general_status = w.status

            # Handle wind data safely
            wind_data = w.wind()
            wind_direction = wind_data.get('deg', 0) if wind_data else 0
            wind_speed = wind_data.get('speed', 0) if wind_data else 0

            humidity = w.humidity
            temperature = w.temperature('celsius')
            temp_max = temperature.get('temp_max', 0)
            temp_min = temperature.get('temp_min', 0)
            temp_normal = temperature.get('temp', 0)

            heat_index = w.heat_index
            clouds = w.clouds

            # Handle pressure data safely
            pressure_data = w.pressure
            pressure = pressure_data.get('press', 0) if pressure_data else 0

            visibility_distance = w.visibility_distance
            sunrise_time = w.sunrise_time(timeformat='iso')
            sunset_time = w.sunset_time(timeformat='iso')

        except Exception as data_extract_error:
            logging.error(f"Error extracting weather data for '{country_or_city_input}': {data_extract_error}")
            return render_template("dashboard.html", error="Please enter a valid city name!")

        # Store weather data in database - only if everything succeeded
        try:
            unique_id = get_current_user_unique_id(session.get('email'))

            store_weather_data_db(
                email=session.get('email'),
                unique_id=unique_id,
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

            # Log successful weather fetch
            local_time = current_local_time()
            stored_data = get_current_query_data(unique_id)
            if stored_data:
                store_log_data_db(
                    stored_data[0],
                    stored_data[1],
                    stored_data[2],
                    local_time,
                    "Openweather api fetch success")

        except Exception as db_error:
            logging.error(f"Error storing weather data: {db_error}")
            # Continue execution even if database storage fails

        # Get additional data - only if weather succeeded
        get_map = get_map_data()
        imges = get_pexels_data()
        near_places = show_near_places()
        event_list = event_data()

        # Validate additional data and provide defaults
        if isinstance(get_map, str):  # Error message returned
            logging.error(f"Map data error: {get_map}")
            map_html = "<div>Map unavailable</div>"
            date = "N/A"
            time = "N/A"
            country_code = "N/A"
        else:
            map_html = get_map[0]
            date = get_map[1]
            time = get_map[2]
            country_code = get_map[3]

        # Provide default images if fetch failed
        if not imges or len(imges) < 5:
            default_img = {"img_name": "No image available", "url": "#"}
            imges = [default_img] * 5

        # Provide default near places if fetch failed
        if not near_places or len(near_places) < 5:
            default_place = {"city": "N/A", "distance": "N/A"}
            near_places = [default_place] * 5

        # Provide default events if fetch failed
        if not event_list or len(event_list) < 6:
            default_event = {
                "name": "No events available",
                "url": "#",
                "time": "N/A",
                "venue": "N/A",
                "date": "N/A",
                "img": "#"
            }
            event_list = [default_event] * 6

        # Only reach here if weather data was successfully fetched
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
                               map_html=map_html,
                               date=date,
                               time=time,
                               country_code=country_code,

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
                               nedar_place_five_distance=near_places[4]["distance"],

                               first_event_name=event_list[0]["name"],
                               first_event_url=event_list[0]["url"],
                               first_event_start_time=event_list[0]["time"],
                               first_event_venue=event_list[0]["venue"],
                               first_event_date=event_list[0]["date"],
                               first_event_img=event_list[0]["img"],
                               second_event_name=event_list[1]["name"],
                               second_event_url=event_list[1]["url"],
                               second_event_start_time=event_list[1]["time"],
                               second_event_venue=event_list[1]["venue"],
                               second_event_date=event_list[1]["date"],
                               second_event_img=event_list[1]["img"],
                               third_event_name=event_list[2]["name"],
                               third_event_url=event_list[2]["url"],
                               third_event_start_time=event_list[2]["time"],
                               third_event_venue=event_list[2]["venue"],
                               third_event_date=event_list[2]["date"],
                               third_event_img=event_list[2]["img"],
                               fourth_event_name=event_list[3]["name"],
                               fourth_event_url=event_list[3]["url"],
                               fourth_event_start_time=event_list[3]["time"],
                               fourth_event_venue=event_list[3]["venue"],
                               fourth_event_date=event_list[3]["date"],
                               fourth_event_img=event_list[3]["img"],
                               fifth_event_name=event_list[4]["name"],
                               fifth_event_url=event_list[4]["url"],
                               fifth_event_start_time=event_list[4]["time"],
                               fifth_event_venue=event_list[4]["venue"],
                               fifth_event_date=event_list[4]["date"],
                               fifth_event_img=event_list[4]["img"],
                               sixth_event_name=event_list[5]["name"],
                               sixth_event_url=event_list[5]["url"],
                               sixth_event_start_time=event_list[5]["time"],
                               sixth_event_venue=event_list[5]["venue"],
                               sixth_event_date=event_list[5]["date"],
                               sixth_event_img=event_list[5]["img"])

    except Exception as e:
        logging.error(f"Unexpected error in show_page_one_data: {e}")

        # Try to log the error
        try:
            local_time = current_local_time()
            unique_id = get_current_user_unique_id(session.get('email'))
            stored_data = get_current_query_data(unique_id)
            if stored_data:
                store_log_data_db(
                    stored_data[0],
                    stored_data[1],
                    stored_data[2],
                    local_time,
                    str(e))
        except Exception as log_error:
            logging.error(f"Error logging main failure: {log_error}")

        return render_template("dashboard.html", error="Please enter a valid city name!")

def get_pexels_data():
    """
    Fetches image data from Pexels API
    Returns: List of image dictionaries or False on error
    """
    try:
        unique_id = get_current_user_unique_id(session.get('email'))
        country_or_city_input = get_country_or_city_input(unique_id)

        if not country_or_city_input:
            logging.error("No country or city input found for Pexels")
            return False

        API_KEY = os.environ.get("PIXELS_API_KEY")

        if not API_KEY:
            logging.error("Pexels API key not found")
            return False

        api = API(API_KEY)
        img_data = []

        # Search for photos
        try:
            api.search(country_or_city_input, results_per_page=5)
            photos = api.get_entries()
        except Exception as search_error:
            logging.error(f"Pexels search error: {search_error}")
            return False

        if photos:
            for photo in photos:
                try:
                    img_data_dict = {
                        "img_name": photo.img_name() or "Untitled",
                        "url": photo.url() or "#"
                    }
                    img_data.append(img_data_dict)
                    unique_id = get_current_user_unique_id(session.get('email'))

                    # Store in database
                    add_image_data(
                        unique_id,
                        session.get('email'),
                        photo.url(),
                        photo.img_name(),
                        current_local_time(),
                        'Pexels api fetch success')

                except Exception as photo_error:
                    logging.error(f"Error processing photo: {photo_error}")
                    continue

            # Log success
            try:
                unique_id = get_current_user_unique_id(session.get('email'))
                stored_data = get_current_query_data(unique_id)
                if stored_data:
                    local_time = current_local_time()
                    store_log_data_db(
                        stored_data[0],
                        stored_data[1],
                        stored_data[2],
                        local_time,
                        "Pexels api fetch success")
            except Exception as log_error:
                logging.error(f"Error logging Pexels success: {log_error}")

        else:
            logging.warning("No photos found from Pexels")
            return False

        time.sleep(2)  # Rate limiting
        return img_data

    except Exception as e:
        logging.error(f"Pexels function error: {e}")

        # Try to use stored data and log error
        try:
            unique_id = get_current_user_unique_id(session.get('email'))
            stored_image_data = get_image_data(unique_id)
            if stored_image_data:
                add_image_data(
                    session.get('log_data_unique_id'),
                    session.get('email'),
                    stored_image_data[0],
                    stored_image_data[1],
                    current_local_time(),
                    str(e))

            stored_log_data = get_current_query_data(unique_id)
            if stored_log_data:
                local_time = current_local_time()
                store_log_data_db(
                    stored_log_data[0],
                    stored_log_data[1],
                    stored_log_data[2],
                    local_time,
                    str(e))
        except Exception as fallback_error:
            logging.error(f"Error in Pexels fallback: {fallback_error}")

        return False


def show_near_places():
    """
    Fetches nearby cities data
    Returns: List of nearby place dictionaries or False on error
    """
    try:
        wikiDataId = session.get('wikiDataId')

        if not wikiDataId:
            logging.error("No wikiDataId found in session")
            return False

        GEODB_KEY = os.getenv("GEO_DB_KEY")
        if not GEODB_KEY:
            logging.error("GEO_DB_KEY not found for nearby places")
            return False

        conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

        headers = {
            'x-rapidapi-key': GEODB_KEY,
            'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
        }

        try:
            conn.request("GET", f"/v1/geo/cities/{wikiDataId}/nearbyCities?radius=100", headers=headers)
            res = conn.getresponse()

            if res.status != 200:
                logging.error(f"Nearby cities API returned status {res.status}")
                return False

            data = json.loads(res.read().decode("utf-8"))
        except (http.client.HTTPException, json.JSONDecodeError) as e:
            logging.error(f"Error fetching nearby cities: {e}")
            return False

        if "data" not in data:
            logging.warning("No nearby cities data found")
            return False

        city_list = []
        dict_location = data['data']

        for location in dict_location:
            try:
                city_dict = {
                    "city": location.get("city", "Unknown"),
                    "distance": location.get("distance", "N/A")
                }
                city_list.append(city_dict)
                unique_id = get_current_user_unique_id(session.get('email'))
                # Store in database
                add_near_city_data_db(
                    unique_id,
                    session.get('email'),
                    wikiDataId,
                    location.get("city"),
                    location.get("distance"),
                    current_local_time(),
                    "success")
            except Exception as city_error:
                logging.error(f"Error processing nearby city: {city_error}")
                continue

        # Log success
        try:
            unique_id = get_current_user_unique_id(session.get('email'))
            stored_log_data = get_current_query_data(unique_id)
            if stored_log_data:
                local_time = current_local_time()
                store_log_data_db(
                    stored_log_data[0],
                    stored_log_data[1],
                    stored_log_data[2],
                    local_time,
                    "Nearby cities api fetch success")
        except Exception as log_error:
            logging.error(f"Error logging nearby cities success: {log_error}")

        return city_list

    except Exception as e:
        logging.error(f"Near places error: {e}")

        # Try to use stored data and log error
        try:
            unique_id = get_current_user_unique_id(session.get('email'))
            stored_near_cities_data = get_near_cities_data(unique_id)
            if stored_near_cities_data:
                add_near_city_data_db(
                    session.get('log_data_unique_id'),
                    session.get('email'),
                    stored_near_cities_data[0],
                    stored_near_cities_data[1],
                    stored_near_cities_data[2],
                    current_local_time(),
                    str(e))

            stored_log_data = get_current_query_data(unique_id)
            if stored_log_data:
                local_time = current_local_time()
                store_log_data_db(
                    stored_log_data[0],
                    stored_log_data[1],
                    stored_log_data[2],
                    local_time,
                    str(e))
        except Exception as fallback_error:
            logging.error(f"Error in near places fallback: {fallback_error}")

        return False


def event_data():
    """
    Fetches event data from Ticketmaster API
    Returns: List of event dictionaries or False on error
    """
    try:
        unique_id= get_current_user_unique_id(session.get('email'))
        country_or_city_input = get_country_or_city_input(unique_id)

        TICKETMASTER_API_KEY = os.environ.get("TICKETMASTER_API_KEY")

        if not TICKETMASTER_API_KEY:
            logging.error("Ticketmaster API key not found")
            return False

        events_fetcher = EventsFetcher(api_key=TICKETMASTER_API_KEY)

        try:
            events = events_fetcher.get_events(country_or_city_input)
        except Exception as fetch_error:
            logging.error(f"Error fetching events: {fetch_error}")
            return False

        if not events:
            logging.warning("No events found")
            return False

        # Store events in database
        for event in events:
            try:
                unique_id = get_current_user_unique_id(session.get('email'))
                store_event_data_db(
                    unique_id,
                    session.get('email'),
                    event.get("name", "Unknown Event"),
                    event.get("date", "N/A"),
                    event.get("time", "N/A"),
                    event.get("venue", "N/A"),
                    event.get("url", "#"),
                    current_local_time(),
                    "success"
                )
            except Exception as store_error:
                logging.error(f"Error storing event data: {store_error}")
                continue

        # Log success
        try:
            unique_id = get_current_user_unique_id(session.get('email'))
            stored_log_data = get_current_query_data(unique_id)
            if stored_log_data:
                local_time = current_local_time()
                store_log_data_db(
                    stored_log_data[0],
                    stored_log_data[1],
                    stored_log_data[2],
                    local_time,
                    "event data api successfully fetched")
        except Exception as log_error:
            logging.error(f"Error logging events success: {log_error}")

        return events

    except Exception as e:
        logging.error(f"Event data error: {e}")

        # Try to use stored data and log error
        try:
            unique_id = get_current_user_unique_id(session.get('email'))
            stored_log_data = get_current_query_data(unique_id)
            if stored_log_data:
                local_time = current_local_time()
                store_log_data_db(
                    stored_log_data[0],
                    stored_log_data[1],
                    stored_log_data[2],
                    local_time,
                    str(e))

            stored_event_data = get_event_data(unique_id)
            if stored_event_data:
                store_event_data_db(
                    session.get('log_data_unique_id'),
                    session.get('email'),
                    stored_event_data[0],
                    stored_event_data[1],
                    stored_event_data[2],
                    stored_event_data[3],
                    stored_event_data[4],
                    current_local_time(),
                    str(e)
                )
        except Exception as fallback_error:
            logging.error(f"Error in event data fallback: {fallback_error}")

        return False