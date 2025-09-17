import http.client
import json
conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9b7c9d2e99msh91a2a51875d27bcp19318ejsn6e1c032e0a1f",
    'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
}
wikiDataId="Q1094194"

conn.request("GET", f"/v1/geo/cities/{wikiDataId}/nearbyCities?radius=100", headers=headers)

res = conn.getresponse()

data = json.loads(res.read().decode("utf-8"))
list=[]
dict_location=data['data']
for i in dict_location:
    dict={
        "city":i.get("city"),
        "distance":i.get("distance")
    }
    list.append(dict)
    # print(dict)
    # near_cities=i.get("city")
    # distance=i.get("distance")

print("Near Places: ",list)
print("Near Places Length: ",len(list))