import http.client

conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9b7c9d2e99msh91a2a51875d27bcp19318ejsn6e1c032e0a1f",
    'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
}

conn.request("GET", "/v1/geo/cities/Q60/nearbyCities?radius=100", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))