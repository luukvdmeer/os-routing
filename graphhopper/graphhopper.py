import os
import requests

gh_server = os.getenv("GH_SERVER_URL", "http://localhost:8989")

def get_isochrone(coords, vehicle = "car", limit = 600, buckets = 1):

  # Compose request.
  url_type = gh_server + "/isochrone"
  url_coords = "?point=" + str(coords[0]) + "," + str(coords[1])
  url_vehicle = "&vehicle=" + vehicle
  url_limit = "&time_limit=" + str(limit)
  url_bucket = "&buckets=" + str(buckets)
  url_misc = ""
  url = url_type + url_coords + url_vehicle + url_limit + url_bucket + url_misc

  # Send request.
  response = requests.get(url)

  return response.json()

def get_route(coords, vehicle = "car"):

  # Compose request.
  url_type = gh_server + "/route"
  url_coords = "?" + "&".join(["point=" + str(x[0]) + "," + str(x[1]) for x in coords])
  url_vehicle = "&vehicle=" + vehicle
  url_misc = "&points_encoded=false"
  url = url_type + url_coords + url_vehicle + url_misc

  # Send request.
  response = requests.get(url)

  return response.json()