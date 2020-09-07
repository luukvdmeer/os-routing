# GraphHopper

GraphHopper is a Java-based routing engine that can be used either as Java library or server. Here, we explore GraphHopper as a locally hosted server.

- [Homepage](https://www.graphhopper.com/)
- [GitHub](https://github.com/graphhopper/graphhopper)
- [API Documentation](https://docs.graphhopper.com/#tag/Routing-API)

## Setup

The easiest way to set up GraphHopper on your own server is by using the JAR file that they provide. This requires a Java Virtual Environment (JRE). Then, the routing engine can be configured in a step-wise procedure. All steps should be executed in the same working directory. For a full installation guide of GraphHopper, see their [documentation](https://github.com/graphhopper/graphhopper/blob/1.0/docs/web/quickstart.md)

### Download the data

Before setting up GraphHopper, OpenStreetMap data need to be downloaded. This goes fast and easy with [geofabrik](http://download.geofabrik.de/), who provide country wide data in neat `osm.pbf` format. For example, one can download the complete OSM data of Austria in 'only' a 570 MB file.

```bash
wget http://download.geofabrik.de/europe/austria-latest.osm.pbf
```

### Construct the network and start the server

Two additional files are needed to construct the network: the GraphHopper Web Service as jar file, and a default configuration file. This configuration file allows to configure the construction process (e.g. which algorithm to use, which vehicle profile to use, et cetera).

```bash
wget https://graphhopper.com/public/releases/graphhopper-web-1.0.jar
wget https://raw.githubusercontent.com/graphhopper/graphhopper/1.0/config-example.yml
```

Using these files, the GraphHopper routing engine can be started as follows. 

```bash
java -Ddw.graphhopper.datareader.file=austria-latest.osm.pbf -jar *.jar server config-example.yml
```

This will start a local routing server on port 8989.

When executing this for the first time (or after updating the data or configuration file) it will take some time, because the network has to be constructed. Thanks to caching, further starts will only load the network and should be nearly instantaneous. However, this means that after updating the data or changing the configuration, the `graph_cache` folder first has to be removed before restarting the routing engine.

## Functionalities

In GraphHopper, there is a difference in functionalities between their open-source routing engine and their commercial API. Some core features, like matrix calculations and route optimization, are closed-source and only offered in a commercial fashion. See [here](https://www.graphhopper.com/open-source) for details. The route optimization however is still based on an open-source Java library called `jsprit`, but we will not discuss that here.

The open-source GraphHopper routing engine offers the following core services:

- The `route` service finds the cheapest route between locations in the supplied order, based on a defined travel cost.
- The `isochrone` service calculates isochrones (time based) or isodistances (distance based) around a given location, according to a given limit.
- The `map matching` service snaps given GPS trajectories to the road network in the most plausible way.

Most functionalities are demonstrated in the file [demo.py](demo.py). Running it with `python3 demo.py` will:

- Create a route through all locations in `data/stops.csv`, in the supplied order, using the `route` service.
- Compute two isochrones (10 and 5 minutes) around the first location in `data/stops.csv`, using the `isochrone` service.

Execution times will be printed to the console and responses (including maps for the route and isochrones) will be saved in the `response` directory. Make sure to have an GraphHopper server running at port 8989, with a pre-processed road network of Austria.

## Performance

Core functionalities perform as follows:

- Creating a route through all locations in `data/stops.csv` in the supplied order takes +/- **0.06** seconds.
- Computing two isochrones (5 and 10 minutes) for the first location in `data/stops.csv` takes +/- **0.20** seconds.

## Customization

*To be added..*