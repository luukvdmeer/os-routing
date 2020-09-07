# Open Source Routing Machine

The Open Source Routing Machine (OSRM) is a C++ routing engine to calculate shortest paths in road networks.

- [Homepage](http://project-osrm.org/)
- [GitHub](https://github.com/Project-OSRM/osrm-backend)
- [API Documentation](http://project-osrm.org/docs/v5.22.0/api/#general-options)

## Setup

The easiest way to set up OSRM on your own server is by using Docker images that they provide. Obviously, this requires Docker to be installed. Then, the routing engine can be configured in a step-wise procedure. All steps should be executed in the same working directory. For a full installation guide of OSRM, see their [documentation](https://github.com/Project-OSRM/osrm-backend)

### Download the data

Before setting up OSRM, OpenStreetMap data need to be downloaded. This goes fast and easy with [geofabrik](http://download.geofabrik.de/), who provide country wide data in neat `osm.pbf` format. For example, one can download the complete OSM data of Austria in 'only' a 570 MB file.

```bash
wget http://download.geofabrik.de/europe/austria-latest.osm.pbf
```

### Extract the road network

The data includes information which is irrelevant to routing, such as positions of public waste baskets. Also, the data does not conform to a hard standard and important information can be described in various ways. Thus it is necessary to extract the routing data into a normalized format. This is done by the OSRM tool named extractor. It parses the contents of the exported OSM file and writes out routing metadata.

Profiles are used during this process to determine what can be routed along, and what cannot (private roads, barriers etc.). OSRM has three built-in profiles:

- Bicycle
- Car
- Foot 

The [lua-files](https://github.com/Project-OSRM/osrm-backend/tree/master/profiles) belonging to these built-in profiles can be wrangled and extended by users to create custom profiles. See the [documentation](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/profiles.md) for details.

```bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/austria-latest.osm.pbf
```

The flag `-v "${PWD}:/data"` creates the directory `/data` inside the docker container and makes the current working directory `"${PWD}"` available there. Of course, this can be changed into any directory, in case the downloaded data is not stored in the current working directory.


### Pre-process the network

The way in which the network is pre-processed, depends on the algorithm that will be used for routing. The two options are:

- Contraction Hierarchies (CH) which best fits use-cases where query performance is key, especially for large distance matrices.
- Multi-Level Dijkstra (MLD) which best fits use-cases where query performance still needs to be very good; and live-updates to the data need to be made.

#### Contraction Hierarchies

The [contraction hierarchies](https://en.wikipedia.org/wiki/Contraction_hierarchies) algorithm creates shortcuts in a preprocessing phase which are then used during a shortest-path query to skip over unimportant nodes. This is based on the observation that road networks are highly hierarchical. Some intersections, for example highway junctions, are more important and higher up in the hierarchy than for example a junction leading into a dead end. Shortcuts can be used to save the precomputed distance between two important junctions such that the algorithm doesn't have to consider the full path between these junctions at query time. The algorithm does not know about which roads humans consider important (e.g. highways), but is are provided with the graph as input and able to assign importance to vertices using heuristics.

The pre-processing needs to be performed with the `contract` tool of OSRM.

```bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/austria-latest.osrm
```

#### Multi-Level Dijkstra

The Multi-Level Dijkstra algorithm is based on [Customizable Route Planning](https://pdfs.semanticscholar.org/4e8b/939377ec6de2107b4ad5c4ce4a837ed7d8d9.pdf), which is an arc separator type of algorithm. In the first phaes (*partition*), one computes a partition C = (C1,...,Ck) of the nodes into balanced cells while attempting to minimize the number of cut arcs (which connect boundary vertices of different cells). Shortcuts are then added to preserve the distances between the boundary nodes within each cell. This partition does not depend on the cost function. The second phase (*customization*) computes the costs of the clique arcs by processing the cells in bottom-up fashion and in parallel. This structure makes is possible to incorporate a new metric in less than a second, which is fast enough to support, for example, real-time traffic updates.

The partition and customization phases are implemented in separate OSRM tools that need to be executed.

```bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/austria-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/austria-latest.osrm
```

### Start the server

With the constructed network, the OSRM routing engine can be started as follows. 

```bash
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed  --max-table-size=10000 --algorithm mld /data/austria-latest.osrm
```

This will start a local routing server on port 5000. The `--max-table-size` parameter sets the maximum number of nodes to be used when creating cost matrices. By default, this is 100, which is often too small for big data. The `--algorithm` parameter defines the algorithm to be used for finding shortest routes, where `mld` stands for Multi-Level Dijkstra and `ch` for Contraction Hierarchies.

## Functionalities

The OSRM routing engine offers the following services:

- The `nearest` service snaps a single location to the street network and returns the nearest n matches.
- The `route` service finds the cheapest route between locations in the supplied order, based on a defined travel cost.
- The `table` service computes the travel costs between all pairs of given locations.
- The `match` service snaps given GPS points to the road network in the most plausible way.
- The `trip` service solves the Traveling Salesman Problem using a greedy heuristic (farthest-insertion algorithm). 
- The `tile` service generates Mapbox Vector Tiles containing road geometries and metadata that can be used to examine the routing graph.

Most functionalities are demonstrated in the file [demo.py](demo.py). Running it with `python3 demo.py` will:

- Snap all locations in `data/stops.csv` to the network, using the `nearest` service.
- Create a route through all locations in `data/stops.csv`, in the supplied order, using the `route` service.
- Compute a travel time matrix with all locations in `data/stops.csv`, using the `table` service.
- Find the optimal route visiting all locations in `data/stops.csv`, using the `trip` service.

Execution times will be printed to the console and responses (including maps for the routes) will be saved in the `response` directory. Make sure to have an OSRM server running at port 5000, with a pre-processed road network of Austria.

## Performance

Core functionalities perform as follows, using the Multi-Level Dijkstra algorithm with the car profile:

- Snapping all locations in `..data/stops.csv` to the network takes +/- **0.02** seconds.
- Creating a route through all locations in `data/stops.csv` in the supplied order takes +/- **0.08** seconds.
- Computing a travel time matrix with all locations in `data/stops.csv` takes +/- **0.04** seconds.
- Solving the traveling salesman problem with all locations in `data/stops.csv` takes +/- **0.09** seconds.

## Customization

*To be added..*