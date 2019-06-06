from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
import numpy as np
import requests
import json

def coords_from_csv(csv, column_x, column_y, **kwargs):

    """Reads coordinates from a csv file."""

    csv_file       = pd.read_csv(csv, **kwargs)
    coords         = csv_file[[column_x, column_y]].drop_duplicates()
    coords.columns = ['x', 'y']

    return coords


def get_matrix(event, stops, annotations, integers = True):


    """Creates a distance/duration matrix from a set of coordinates, using OSRM."""

    # Set URL composers:
    url_start  = 'http://127.0.0.1:5000/table/v1/driving/' + str(event['y']) + ',' + str(event['x'])

    url_points = ''

    for index, row in stops.iterrows():

        url_points = url_points + ';' + str(row['y']) + ',' + str(row['x'])


    url_end = '?annotations=' + annotations

    # Compose URL
    url_full = url_start + url_points + url_end

    # Request, and get response as json
    response = requests.get(url_full).json()

    # Retrieve only the matrix, as an numpy array
    matrix = np.array(response[str(annotations) + 's'])

    # When integers is True, round the values in the matrix to integers
    if integers:

        matrix = np.around(matrix, decimals = 0)


    # Return the matrix
    return matrix


def create_data_model(matrix, num_vehicles):

    """Stores the data for the problem"""

    data = {}

    data['distance_matrix'] = matrix
    data['num_vehicles']    = num_vehicles
    data['depot']           = 0

    return data


def print_solution(data, manager, routing, solution):

    """Prints solution on console."""

    # Loop over the vehicles to display the optimal route for each of them
    for vehicle_id in range(data['num_vehicles']):

        index          = routing.Start(vehicle_id)
        plan_output    = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0

        while not routing.IsEnd(index):

            plan_output    += ' {} -> '.format(manager.IndexToNode(index))
            previous_index  = index
            index           = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)


        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Duration of the route: {} hours\n'.format(route_distance/60/60)
        
        print(plan_output)




def main(num_vehicles):

    """Solve the CVRP problem."""

    # Event coordinates
    event = pd.Series([48.3151658, 13.8922251], index = ['x', 'y'])

    # Stops coordinates
    stops = coords_from_csv(csv = 'data/stops.csv', column_x = 'stop x', column_y = 'stop y', sep = ';', decimal = ',')

    # Get duration matrix
    matrix = get_matrix(event = event, stops = stops, annotations = 'duration', integers = True)

    # Instantiate the data problem
    data = create_data_model(matrix = matrix, num_vehicles = num_vehicles)

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), 
        data['num_vehicles'], 
        data['depot']
    )

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback
    def distance_callback(from_index, to_index):

        """Returns the distance between the two nodes."""

        # Convert from routing variable Index to distance matrix NodeIndex
        from_node = manager.IndexToNode(from_index)
        to_node   = manager.IndexToNode(to_index)

        return data['distance_matrix'][from_node][to_node]


    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add duration constraint
    dimension_name = 'Duration'

    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3600 * 4,  # vehicle maximum travel duration
        True,  # start cumul to zero
        dimension_name
    )

    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console
    if solution:

        print_solution(data, manager, routing, solution)

    else:

        print('There is no possible solution')


if __name__ == '__main__':

    main(num_vehicles = 10)