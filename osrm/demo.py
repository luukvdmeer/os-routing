import pandas as pd
import folium
import time

import osrm

# Load coordinates of points to visit.
# OSRM needs longitude and latitude coordinates in the order [lon, lat].
# In the CSV the longitudes are in column 'stop y' and latitudes in 'stop x'.
csv = pd.read_csv("../data/stops.csv", sep = ";", decimal = ",")
csv = csv[["stop x", "stop y"]].drop_duplicates()
pts = [[lon, lat] for lon, lat in zip(csv["stop y"], csv["stop x"])]

# Retrieve the travel time matrix.
t0 = time.time()
matrix = osrm.get_matrix(pts)
t1 = time.time()
t = t1 - t0
print("Travel time matrix retrieved in {} seconds".format(t))

# Retrieve the route through all points.
# This route will visit the points in the order they are provided.
t0 = time.time()
route = osrm.get_route(pts)
t1 = time.time()
t = t1 - t0
print("Route retrieved in {} seconds".format(t))

# Save route as map.
m = folium.Map(location = pts[0][::-1], tiles = "cartodbpositron")
folium.GeoJson(route["routes"][0]["geometry"]).add_to(m)
m.save("map.html")
print("Route map saved as map.html")