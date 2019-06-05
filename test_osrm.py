import pandas as pd
import routing
import json

# Event coordinates
event = pd.Series([48.3151658, 13.8922251], index = ['x', 'y'])

# Stops coordinates
stops = routing.read_coords(file = 'data/stops.csv', column_x = 'stop x', column_y = 'stop y', sep = ';', decimal = ',')

# Get route
route = routing.get_route(event = event, stops = stops, engine = 'OSRM')

# Save on disk
with open('outputs/route_osrm_encoded.json', 'w') as json_file:
	json.dump(route, json_file)

print(route)

# Get route without encoded geometry
route = routing.get_route(event = event, stops = stops, engine = 'OSRM', geometry_encoded = False)

# Save on disk
with open('outputs/route_osrm.json', 'w') as json_file:
	json.dump(route, json_file)

print(route)

# Get duration matrix
matrix = routing.get_matrix(event = event, stops = stops, engine = 'OSRM', annotations = 'duration')

# Save on disk
with open('outputs/matrix_osrm.json', 'w') as json_file:
	json.dump(matrix, json_file)

print(matrix)