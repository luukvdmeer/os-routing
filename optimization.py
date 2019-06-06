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


def loads_from_csv(csv, column_x, column_y, **kwargs):

    """Retrieves the number of people to pick up for each stop from a csv file."""

    csv_file = pd.read_csv(csv, **kwargs)
    loads    = csv_file.groupby([column_x, column_y]).size().tolist()

    return loads



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


def create_data_model(matrix, loads, vehicles_number, vehicles_capacities):

    """Stores the data for the problem"""

    data = {}

    data['matrix']              = matrix
    data['loads']               = loads
    data['vehicles_capacities'] = vehicles_capacities
    data['vehicles_number']     = vehicles_number
    data['depot']               = 0

    return data


def get_solution(data, manager, routing, solution, display_result = True):

    """Prints solution on console."""

    if display_result:

        # Set initial values for total duration and total load of all routes
        total_duration = 0
        total_load     = 0

        # Loop over the vehicles to display the optimal route for each of them
        for vehicle_id in range(data['vehicles_number']):

            index          = routing.Start(vehicle_id) # Index of the node where the route for this vehicle starts
            plan_output    = 'Route for vehicle {}:\n'.format(vehicle_id) # First part of the displayed output for this vehicle
            route_duration = 0 # Initial value for the total duration of the single route
            route_load     = 0 # Initial value for the total load of the single route

            # Loop over all separate nodes that are visited by this vehicle
            while not routing.IsEnd(index):

                node_index      = manager.IndexToNode(index) # Index of the visited node
                route_load     += data['loads'][node_index] # Update the route_load with the amount of people entering the bus at this node
                plan_output    += ' {0} Load({1}) -> '.format(node_index, route_load) # Display the node index and the load of the bus after visiting this node
                previous_index  = index # Set the current node index to be the 'previous index'
                index           = solution.Value(routing.NextVar(index)) # Set the next node index to be the new 'index'
                route_duration += routing.GetArcCostForVehicle(previous_index, index, vehicle_id) # Update the route duration


            plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index), route_load) # Display node index and load for last part of the route
            plan_output += 'Duration of the route: {} hours\n'.format(route_duration / 3600) # Display the total duration of the route, in hours
            plan_output += 'Load of the route: {} people\n'.format(route_load) # Display the total load of the route
        
            print(plan_output) # Print the output

            total_duration += route_duration # Update the total duration of all routes
            total_load     += route_load # Update the total load of all routes

        print('Total duration of all routes: {} hours'.format(total_duration / 3600)) # Print the total duration of all routes, in hours
        print('Total load of all routes: {} people'.format(total_load)) # Print the total load of all routes
    

    else:

        all_routes = [] # Empty list to store the route lists of all routes

        # Loop over the vehicles to store the optimal route for each of them
        for vehicle_id in range(data['vehicles_number']):

            index = routing.Start(vehicle_id) # Index of the node where the route for this vehicle starts
            route = [] # Empty list to store the indices of the nodes that are visited by this vehicle

            # Loop over all separate nodes that are visited by this vehicle
            while not routing.IsEnd(index):

                route.append(manager.IndexToNode(index)) # Add the index of the visited node to the route list
                index = solution.Value(routing.NextVar(index)) # Set the next node index to be the new 'index'


            route.append(manager.IndexToNode(index)) # Add the index of the final node to the route list
            all_routes.append(route) # Add the completed route list to the all_routes list

        return all_routes


def main():

    """Solve the CVRP problem."""

    # Event coordinates
    event = pd.Series([48.3151658, 13.8922251], index = ['x', 'y'])

    # Stops coordinates
    coords = coords_from_csv(csv = 'data/stops.csv', column_x = 'stop x', column_y = 'stop y', sep = ';', decimal = ',')

    # Get duration matrix
    matrix = get_matrix(event = event, stops = coords, annotations = 'duration', integers = True)

    # Loads per stop
    loads = loads_from_csv(csv = 'data/stops.csv', column_x = 'stop x', column_y = 'stop y', sep = ';', decimal = ',')

    # Add a load of zero to the event
    loads.insert(0, 0)

    # Define the number of vehicles
    vehicles_number = 10

    # Define the capacity of each vehicle
    vehicles_capacities = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

    # Instantiate the data problem
    data = create_data_model(matrix, loads, vehicles_number, vehicles_capacities)

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data['matrix']), 
        data['vehicles_number'], 
        data['depot']
    )

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    ## ARC COSTS
    # Create and register a duration callback
    def duration_callback(from_index, to_index):

        """Returns the duration between the two nodes."""

        # Convert from routing variable Index to matrix NodeIndex
        from_node = manager.IndexToNode(from_index)
        to_node   = manager.IndexToNode(to_index)

        return data['matrix'][from_node][to_node]


    duration_callback_index = routing.RegisterTransitCallback(duration_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(duration_callback_index)

    ## CAPACITY CONSTRAINTS
    # Create and register load callback
    def load_callback(index):

        """Returns the number of people to be picked up at a node"""

        # Convert from routing variable Index to loads NodeIndex
        node = manager.IndexToNode(index)

        return data['loads'][node]

    load_callback_index = routing.RegisterUnaryTransitCallback(load_callback)

    # Add capacity constraint
    routing.AddDimensionWithVehicleCapacity(
        load_callback_index,
        0,  # No waiting times at stops
        data['vehicles_capacities'], # Vehicle maximum capacity
        True,  # Start cumulative to zero
        'Capacity' # Dimension name
    )

    ## SOLVE
    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console
    if solution:

        get_solution(data, manager, routing, solution, display_result = False)

    else:

        print('There is no possible solution')


if __name__ == '__main__':

    main()