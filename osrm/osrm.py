import os
import requests

osrm_server = os.getenv("OSRM_SERVER_URL", "http://localhost:5000")

def get_matrix(coords, cost = "duration"):

  # Compose request.
  url_type = osrm_server + "/table/v1/driving/"
  url_coords = ";".join([str(x[0]) + "," + str(x[1]) for x in coords])
  url_cost = "?annotations=" + cost
  url = url_type + url_coords + url_cost

  # Send request.
  response = requests.get(url)

  return response.json()

def get_route(coords):

  # Compose request.
  url_type = osrm_server + "/route/v1/driving/"
  url_coords = ";".join([str(x[0]) + "," + str(x[1]) for x in coords])
  url_options = "?overview=full&geometries=geojson"
  url = url_type + url_coords + url_options

  # Send request.
  response = requests.get(url)

  return response.json()

def optimize_route(coords):

  # Compose request.
  url_type = osrm_server + "/trip/v1/driving/"
  url_coords = ";".join([str(x[0]) + "," + str(x[1]) for x in coords])
  url_options = "?overview=full&geometries=geojson"
  url = url_type + url_coords + url_options

  # Send request.
  response = requests.get(url)

  return response.json()

def snap_points(coords):

  result = []

  for x in coords:

    # Compose request.
    url_type = osrm_server + "/nearest/v1/driving/"
    url_coords = str(x[0]) + "," + str(x[1])
    url_options = "?number=1"
    url = url_type + url_coords + url_options

    # Send request.
    response = requests.get(url)

    result.append(response.json())

  return result