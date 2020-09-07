import os
import requests

osrm_server = os.getenv("OSRM_SERVER_URL", "http://localhost:5000")

def get_matrix(coords, cost = "duration"):
  """
  Retrieves a matrix from the OSRM routing engine, describing the travel cost between two
  locations, for each possible combination of locations.

  Args:
    coords (list): List of coordinate pairs, where each coordinate pair describes a
      location in geographical space and is a list [a, b] with a and b being respectively 
      the longitude and latitude coordinates of the location.
    cost (str): The type of travel cost to be used, either 'duration' or 'distance'.

  Returns:
    list: A matrix structured as a list of lists.

  """

  # Compose request.
  url_type = osrm_server + "/table/v1/driving/"
  url_coords = ";".join([str(x[0]) + "," + str(x[1]) for x in coords if len(x) == 2])
  url_cost = "?annotations=" + cost
  url = url_type + url_coords + url_cost

  # Send request.
  response = requests.get(url)

  return response.json()

def get_route(coords):
  """
  Retrieves the shortest route between multiple locations from the OSRM routing engine.
  The locations will be visited in the order they are provided.

  Args:
    coords (list): List of coordinate pairs, where each coordinate pair describes a
      location in geographical space and is a list [a, b] with a and b being respectively 
      the longitude and latitude coordinates of the location. Dummy locations, with a
      coordinate value of [None] instead of [a, b], will be ignored.

  Returns:
    dict: An OSRM route result - http://project-osrm.org/docs/v5.5.1/api/#result-objects.
  
  """

  # Compose request.
  url_type = osrm_server + "/route/v1/driving/"
  url_coords = ";".join([str(x[0]) + "," + str(x[1]) for x in coords if len(x) == 2])
  url_options = "?overview=full&geometries=geojson"
  url = url_type + url_coords + url_options

  # Send request.
  response = requests.get(url)

  return response.json()