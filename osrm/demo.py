import pandas as pd
import folium
import json
import time

import osrm

# Load coordinates of points to visit.
# OSRM needs longitude and latitude coordinates in the order [lon, lat].
# In the CSV the longitudes are in column 'stop y' and latitudes in 'stop x'.
csv = pd.read_csv("../data/stops.csv", sep = ";", decimal = ",")
csv = csv[["stop x", "stop y"]].drop_duplicates()
pts = [[lon, lat] for lon, lat in zip(csv["stop y"], csv["stop x"])]

## NEAREST SERVICE ##

# Snap all points to the network, finding the nearest matching network node.
t0 = time.time()
snap = osrm.snap_points(pts)
t1 = time.time()
t = t1 - t0
print("Points snapped to network in {} seconds".format(t))

# Save as JSON.
with open("response/snap.json", "w") as f:
  json.dump(snap, f, indent = 2)

## ROUTE SERVICE ##

# Retrieve the route through all points.
# This route will visit the points in the order they are provided.
t0 = time.time()
route = osrm.get_route(pts)
t1 = time.time()
t = t1 - t0
print("Route retrieved in {} seconds".format(t))

# Save as html.
m = folium.Map(location = pts[0][::-1], tiles = "cartodbpositron")
folium.GeoJson(route["routes"][0]["geometry"]).add_to(m)
m.save("response/route.html")

# Save as JSON.
with open("response/route.json", "w") as f:
  json.dump(route, f, indent = 2)

## TABLE SERVICE ##

# Retrieve the travel time matrix.
t0 = time.time()
matrix = osrm.get_matrix(pts)
t1 = time.time()
t = t1 - t0
print("Travel time matrix retrieved in {} seconds".format(t))

# Save as JSON.
with open("response/matrix.json", "w") as f:
  json.dump(matrix, f, indent = 2)

## TRIP SERVICE ##

# Retrieve the optimal route through all points.
t0 = time.time()
tsp = osrm.optimize_route(pts)
t1 = time.time()
t = t1 - t0
print("Traveling salesman problem solved in in {} seconds".format(t))

# Save TSP result as map.
m = folium.Map(location = pts[0][::-1], tiles = "cartodbpositron")
folium.GeoJson(tsp["trips"][0]["geometry"]).add_to(m)
m.save("response/tsp.html")

# Save as JSON.
with open("response/tsp.json", "w") as f:
  json.dump(tsp, f, indent = 2)