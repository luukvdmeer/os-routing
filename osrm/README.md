# Open Source Routing Machine

The Open Source Routing Machine (OSRM) is a modern C++ routing engine to calculate shortest paths in road networks.

- [Homepage](http://project-osrm.org/)
- [GitHub](https://github.com/Project-OSRM/osrm-backend)
- [API Documentation](http://project-osrm.org/docs/v5.22.0/api/#general-options)

## Setup

The easiest way to set up OSRM on your own server is by using Docker images that they provide. Obviously, this requires Docker to be installed.

Before setting up OSRM, OpenStreetMap data need to be downloaded. This goes fast and easy with [geofabrik](http://download.geofabrik.de/), who provide country wide data in neat osm.pbf format. For example, one can download the complete OSM data of Austria in 'only' a 570 MB file.

```bash
wget http://download.geofabrik.de/europe/austria-latest.osm.pbf
```

With OSRM, these data now need to be converted into a network structure suitable for routing. One needs to specify the profile that is going to be used for this, i.e. for which type of vehicle the network is created. OSRM has three built-in profiles:

- Bicycle
- Car
- Foot 

The `.lua` files belonging to these built-in profiles can be wrangled and extended by users to create custom profiles.

Then, in three steps the data is pre-processed and analysis ready. The data pre-processing only has to be done when the new data is used (i.e. when setting up OSRM for the first time or when updating to the most recent data).

```bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/austria-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/austria-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/austria-latest.osrm
```

The flag `-v "${PWD}:/data"` creates the directory `/data` inside the docker container and makes the current working directory `"${PWD}"` available there. Of course, this can be changed into any directory, in case the downloaded data is not stored in the current working directory.

For a full installation guide of OSRM, see their [documentation](https://github.com/Project-OSRM/osrm-backend)

## Run

With the pre-processed data, the OSRM routing engine can be started as follows. 

```bash
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed  --max-table-size=10000 --algorithm mld /data/austria-latest.osrm
```

This will start a local routing server on port 5000. The `--max-table-size` parameter sets the maximum number of nodes to be used when creating cost matrices. By default, this is 100, which is often too small for big data. The `--algorithm` parameter defines the algorithm to be used for finding shortest routes. In this case, it is the recommende Multi-Level Dijkstra (MLD) algorithm.

## Test

Running `python3 demo.py` will:

- Create a travel time matrix with all locations in `../data/stops.csv`
- Create a route through all locations in `../data/stops.csv`

Execution times will be printed to the console and the map of the created route will be saved as `map.html`. Make sure to have an OSRM server running at port 5000.

## Performance

Core functionalities perform as follows:

- A travel time matrix with all locations in `../data/stops.csv` takes +/- **0.044** seconds.
- A route through all locations in `../data/stops.csv` takes +/- **0.089** seconds.

## Customization

*To be added..*