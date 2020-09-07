import pandas as pd
import folium
import json
import time

import graphhopper

# Load coordinates of points to visit.
# GraphHopper needs longitude and latitude coordinates in the order [lat, lon].
# In the CSV the longitudes are in column 'stop y' and latitudes in 'stop x'.
csv = pd.read_csv("../data/stops.csv", sep = ";", decimal = ",")
csv = csv[["stop x", "stop y"]].drop_duplicates()
pts = [[lat, lon] for lat, lon in zip(csv["stop x"], csv["stop y"])]

## ROUTE SERVICE ##

# Retrieve the route through all points.
# This route will visit the points in the order they are provided.
t0 = time.time()
route = graphhopper.get_route(pts)
t1 = time.time()
t = t1 - t0
print("Route retrieved in {} seconds".format(t))

# Save as html.
m = folium.Map(location = pts[0], tiles = "cartodbpositron")
folium.GeoJson(route["paths"][0]["points"]).add_to(m)
m.save("response/route.html")

# Save as JSON.
with open("response/route.json", "w") as f:
  json.dump(route, f, indent = 2)

## ISOCHRONE SERVICE ##

# Retrieve the travel time isochrones.
t0 = time.time()
iso = graphhopper.get_isochrone(pts[0], limit = 600, buckets = 2)
t1 = time.time()
t = t1 - t0
print("Isochrones retrieved in {} seconds".format(t))

# Save isochrones as map.
m = folium.Map(location = pts[0], tiles = "cartodbpositron")
folium.GeoJson(iso["polygons"][0]).add_to(m)
folium.GeoJson(iso["polygons"][1]).add_to(m)
m.save("response/iso.html")

# Save as JSON.
with open("response/iso.json", "w") as f:
  json.dump(iso, f, indent = 2)



