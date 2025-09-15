import time

import requests
import os
import http.client
from dotenv import load_dotenv
load_dotenv()
import json
city = "Milan"
GEODB_KEY=os.getenv("GEO_DB_KEY")
OPENWEATHER_KEY=os.getenv("OPENWEATHER")
import urllib.parse


input="London"
conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9b7c9d2e99msh91a2a51875d27bcp19318ejsn6e1c032e0a1f",
    'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
}
# encoded_country=urllib.parse.quote(country)
# conn.request("GET", f"/v1/geo/countries?namePrefix={input}", headers=headers)
# res = conn.getresponse()
# data = res.read()
# data=data.decode("utf-8")
# data_dict = json.loads(data)
# if data_dict["data"]:
#     country_code=data_dict["data"][0]["code"]
#     print("Country:",data_dict)
# else:
#     conn.request("GET", f"/v1/geo/cities?namePrefix={input}", headers=headers)
#     res_for_city = conn.getresponse()
#     city_data = res_for_city.read()
#     city_data=city_data.decode("utf-8")
#     print(city_data)
#     city_data_dict = json.loads(city_data)
#
#
#
#     print(city_data_dict)
#     country_code_by_city=city_data_dict["data"][0]["countryCode"]
#     print("City:",country_code_by_city)
# optimize code for get country code
# conn.request("GET", f"/v1/geo/cities?namePrefix={input}", headers=headers)
# res = conn.getresponse()
# city_data = res.read().decode("utf-8")
# city_data_dict = json.loads(city_data)
#
# if city_data_dict["data"]:
#     country_code = city_data_dict["data"][0]["countryCode"]
#     print("Country Code:", country_code)
# else:
#     print("No match found")




#To country wikiDataId
#
# conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")
#
# headers = {
#     'x-rapidapi-key': "9b7c9d2e99msh91a2a51875d27bcp19318ejsn6e1c032e0a1f",
#     'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
# }
#
# conn.request("GET", f"/v1/geo/countries/{country_code}", headers=headers)
#
# res = conn.getresponse()
# data = res.read()
# data=data.decode("utf-8")
# data_dict = json.loads(data)
# wikiDataId=data_dict["data"]["wikiDataId"]





#
# conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")
#
# headers = {
#     'x-rapidapi-key': GEODB_KEY,
#     'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
# }
#
# conn.request("GET", "/v1/geo/cities/{wikiDataId}/dateTime", headers=headers)
#
# res = conn.getresponse()
# city_data_time = res.read()
#
# print(city_data_time.decode("utf-8"))


def get_local_time(user_input: str):
    conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

    encoded_input=urllib.parse.quote(user_input)

    # 1) Always search in cities endpoint
    conn.request("GET", f"/v1/geo/cities?namePrefix={encoded_input}", headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    print(data)

    if "data" not in data or not data["data"]:
        return f"No results found for {user_input}"

    first = data["data"][0]
    wikiDataId = first.get("wikiDataId")
    country_code = first.get("countryCode")
    city_name = first.get("city")
    lat=first.get("latitude")
    lon=first.get("longitude")

    # 2) Wait a bit (avoid BASIC plan rate limit)
    time.sleep(1)

    # 3) Get local time for that city
    conn.request("GET", f"/v1/geo/cities/{wikiDataId}/dateTime", headers=headers)
    res = conn.getresponse()
    time_data = json.loads(res.read().decode("utf-8"))

    country_date=time_data.get("data").split("T")[0]
    country_time=time_data.get("data").split("T")[1].split("+")[0]

    return {
        "input": user_input,
        "matched_city": city_name,
        "country_code": country_code,
        "local_time": time_data.get("data"),
        "lat": lat,
        "lon": lon,
        "country_date":country_date,
        "country_time":country_time
    }

# 🔎 Example usage
# print(get_local_time("Sydney"))   # city
print(get_local_time("Sydney"))






# wikiDataId=data_dict["data"]["wikiDataId"]
# print(wikiDataId)

# dic={"data":{"capital":"Washington","code":"US","callingCode":"+1","currencyCodes":["USD"],"flagImageUri":"http://commons.wikimedia.org/wiki/Special:FilePath/Flag%20of%20the%20United%20States.svg","name":"United States","numRegions":57,"wikiDataId":"Q30"}}
#
# print(dic["data"]["wikiDataId"])

