# Open Source Routing Engines
This repository contains scripts, data and output files meant to test different open source routing engines in Austria. The tested engines (for now up to a very basic level) are the following:

- GraphHopper
- Open Source Routing Machine (OSRM)

More advanced tests, and more engines will be added.

Furthermore, the online Leaflet Routing Machine, which uses the OSRM API in the background, was tested.

The steps are described for Ubuntu 16.04, but will with some modifications probably not be too different for other operating systems.

## GraphHopper
### Setup
To setup the Graphhopper routing engine in the easiest way, you need a Java Runtime Environment (JRE). Once/if you have that, follow the following steps.

1. Get the [GraphHopper Web Service](https://github.com/graphhopper/graphhopper/blob/master/README.md#get-started) as jar file, and store this jar file in a directory of choice. 

```bash
wget https://graphhopper.com/public/releases/graphhopper-web-0.12.0.jar
```

2. Download this [configuration file](https://raw.githubusercontent.com/graphhopper/graphhopper/master/config-example.yml), and store it in the same directory.

3. Download OpenStreetMap extracts for the area of interest, for example from [Geofabrik](http://download.geofabrik.de/). Store it again in the same directory.

```bash
wget http://download.geofabrik.de/europe/austria-latest.osm.pbf
```

### Run
In a terminal window, navigate to the directory where you stored all the files during setup, and start the GraphHopper routing engine by running the following command. This will start a local routing server on port 8989.

```bash
java -Dgraphhopper.datareader.file=austria-latest.osm.pbf -jar *.jar server config-example.yml
```

### Test
To test the GraphHopper routing engine, clone this GitHub repository, and run the script `test_gh.py`. This will create the shortest route from a given event location through all the stops in the `stops.csv` file in the `/data` directory. For now, the stops will be visited in the order they appear in the csv file. Two output files that contain the same route will be saved in the `/output` directory. One of them is a json file with the geometries stored in geojson format, the other is a json file with the geometries stored as string-encoded polylines.

### More information
- [GitHub](https://github.com/graphhopper/graphhopper)
- [API Documentation](https://docs.graphhopper.com/)

## OSRM
### Setup
To setup the OSRM routing engine in the easiest way, you need to have Docker installed. Once/if you have that, follow the following steps.

1. Download OpenStreetMap extracts for the area of interest, for example from [Geofabrik](http://download.geofabrik.de/). Store it in a directory of choice.

```bash
wget http://download.geofabrik.de/europe/austria-latest.osm.pbf
```

2. In a terminal window, navigate to the directory where you stored the OpenStreetMap extract, and pre-process the data. This will create a graph structure from the street network, according to the car profile. The flag `-v "${PWD}:/data"` creates the directory `/data` inside the docker container and makes the current working directory `"${PWD}"` available there.

```bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/austria-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/austria-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/austria-latest.osrm
```

### Run
In a terminal window, navigate to the directory where you stored the files during setup, and start the OSRM routing engine by running the following command. This will start a local routing server on port 5000.

```bash
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/austria-latest.osrm
```

### Test
To test the OSRM routing engine, clone this GitHub repository, and run the script `test_osrm.py`. This will create the shortest route from a given event location through all the stops in the `stops.csv` file in the `/data` directory. For now, the stops will be visited in the order they appear in the csv file. Two output files that contain the same route will be saved in the `/output` directory. One of them is a json file with the geometries stored in geojson format, the other is a json file with the geometries stored as string-encoded polylines.

### More information
- [GitHub](https://github.com/Project-OSRM/osrm-backend)
- [API Documentation](http://project-osrm.org/docs/v5.22.0/api/#general-options)

## Leaflet Routing Machine
### Setup
For now, this works without setting anything up locally. It uses the OSRM API in the background.

### Test
The script `test_leaflet.html` is a minimal HTML required to create an interactive Leaflet map with routing function. By default, it will show the shortest route between Z_GIS/Techno_Z in Salzburg, and the Tabakfabrik in Linz, but this can be change interactively. See the result [here](https://luukvdmeer.github.io/).

### More information
- [GitHub](https://github.com/perliedman/leaflet-routing-machine)
- [API Documentation](http://www.liedman.net/leaflet-routing-machine/api/)

## pgrouting
### Setup
To setup pgrouting, you need to have PostgreSQL installed. Once/if you have that, follow the following steps.

1. Install PostGIS, pgrouting, osm2pgrouting and osmctools. If you have another version than PostgreSQL 11, replace the 11 with your version.

```bash
sudo apt-get install postgis 
sudo apt-get install postgresql-11-pgrouting
sudo apt-get install osm2pgrouting
sudo apt-get install osmctools
```

2. Create a database

```bash
sudo -u postgres createdb <dbname>
```

3. Download osm data with the Overpass API. Store it in a directory of choice.

```bash
wget -O linz-umgebung.osm 'https://overpass-api.de/api/map?bbox=13.2,47.6,14.5,48.6'
```

4. Write data to database

```bash
osm2pgrouting --f linz-umgebung.osm --conf /usr/share/osm2pgrouting/mapconfig.xml --dbname test_pgr --username username --password password --clean
```

*TO BE CONTINUED..*

