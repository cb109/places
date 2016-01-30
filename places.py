#!/bin/python3
"""Create a google map page with places as specified by a .csv file."""

# Based on this awesome example:
# http://stackoverflow.com/questions/22342097/is-it-possible-to-create-a-google-map-from-python

import csv
import logging
import sys

import pygeolib
from pygeocoder import Geocoder

USAGE = __doc__ + "\n\n" + "python places.py <my-visited-places.csv>"

DEFAULT_OUTPUTFILE = "map.html"

MARKER_TEMPLATE = """
new google.maps.Marker({{
  position: new google.maps.LatLng({lat}, {lon}),
  map: map
}});
"""

PAGE_TEMPLATE = """
<html>
  <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false">
  </script>
  <div id="map-canvas" style="height: 100%; width: 100%"></div>
  <script type="text/javascript">
    var map;
    function show_map() {{
      map = new google.maps.Map(document.getElementById("map-canvas"), {{
        zoom: 8,
        center: new google.maps.LatLng({center_lat}, {center_long})
      }});
      {markers_code}
    }}
    google.maps.event.addDomListener(window, 'load', show_map);
  </script>
</html>
"""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("places")


class Map(object):
    """
    Represents a Map as defined by the Google Maps API.

    It contains custom markers and returns itself as valid html and
    javascript when cast to a string.
    """
    def __init__(self):
        self._points = []

    def add_point(self, coordinates):
        self._points.append(coordinates)

    def __str__(self):
        if not self._points:
            return "No places to show. Check your .csv file."
        center_lat = sum((x[0] for x in self._points)) / len(self._points)
        center_long = sum((x[1] for x in self._points)) / len(self._points)
        markers_code = "\n".join(
            [MARKER_TEMPLATE.format(lat=x[0], lon=x[1])
             for x in self._points])
        return PAGE_TEMPLATE.format(center_lat=center_lat,
                                    center_long=center_long,
                                    markers_code=markers_code)


def read_places_from_file(csvfile):
    """The .csv must have a single column with city names."""
    with open(csvfile) as f:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(f.read())
    with open(csvfile) as f:
        reader = csv.reader(f, delimiter=dialect.delimiter)
        for row in reader:
            place_column = row[0]
            yield(place_column)


def get_geocoordinates_for_place(place):
    """Will return None if it can't resolve to coordinates."""
    try:
        coords = Geocoder.geocode(str(place)).coordinates
        log.info("Found coordinates for: " + str(place))
        return coords
    except pygeolib.GeocoderError:
        log.error("Could not get coordinates for: " + str(place))
        return None


def visualize(csvfile):
    """Visualize places from .csv as google maps html page."""

    log.info("Reading: " + str(csvfile))
    places = read_places_from_file(csvfile)
    unique_places = list(set(list(places)))
    sorted_places = sorted(unique_places)
    log.info("Read {0} unique places.".format(len(sorted_places)))

    log.info("Querying coordinates.")
    points = []
    for place in sorted_places:
        point = get_geocoordinates_for_place(place)
        if point:
            points.append(point)

    log.info("Assembling map.")
    custom_map = Map()
    for point in points:
        custom_map.add_point(point)

    log.info("Writing results.")
    with open(DEFAULT_OUTPUTFILE, "w") as out:
        out.write(str(custom_map))

    log.info("Map written to: " + DEFAULT_OUTPUTFILE)
    log.info("Open it in a web browser to see the map.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        log.info(USAGE)
    csvfile = args[0]
    visualize(csvfile)
