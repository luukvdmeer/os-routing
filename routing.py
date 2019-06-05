import pandas as pd 
import requests
import json

def coords_from_csv(csv, column_x, column_y, **kwargs):

	csv_file = pd.read_csv(csv, **kwargs)
	coords = csv_file[[column_x, column_y]].drop_duplicates()
	coords.columns = ['x', 'y']

	return(coords)


def get_route(event, stops, engine, geometry_encoded = True):

	# Set URL composers:
	if engine in ['graphhopper', 'gh']:

		separator = '%2C'

		url_start = 'http://localhost:8989/route?point=' + str(event['x']) + separator + str(event['y'])

		url_points = ''
		for index, row in stops.iterrows():
			url_points = url_points + '&point=' + str(row['x']) + separator + str(row['y'])

		url_end = '&vehicle=car'
		if not geometry_encoded:
			url_end = url_end + '&points_encoded=false'

	elif engine in ['osrm', 'OSRM']:

		url_start = 'http://127.0.0.1:5000/route/v1/driving/' + str(event['y']) + ',' + str(event['x'])

		url_points = ''
		for index, row in stops.iterrows():
			url_points = url_points + ';' + str(row['y']) + ',' + str(row['x'])

		url_end = '?steps=true&overview=full'
		if not geometry_encoded:
			url_end = url_end + '&geometries=geojson'

	# Compose URL
	url_full = url_start + url_points + url_end

	# Request
	response = requests.get(url_full)

	# Load as json
	route = response.json()

	return(route)


def get_matrix(event, stops, engine, annotations):

	# Set URL composers:
	if engine in ['graphhopper', 'gh']:

		return 'For now, matrices can only be produces with the OSRM engine'

	elif engine in ['osrm', 'OSRM']:

		url_start = 'http://127.0.0.1:5000/table/v1/driving/' + str(event['y']) + ',' + str(event['x'])

		url_points = ''
		for index, row in stops.iterrows():
			url_points = url_points + ';' + str(row['y']) + ',' + str(row['x'])

		url_end = '?annotations=' + annotations

	# Compose URL
	url_full = url_start + url_points + url_end

	# Request
	response = requests.get(url_full)

	# Load as json
	matrix = response.json()

	return(matrix)