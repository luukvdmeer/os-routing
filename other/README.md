# Other tests

Here are just some code and text snippets that resulted from unfinished tests of several other open-source routing software.

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