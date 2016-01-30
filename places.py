#!/bin/python3
"""Create a google map page with places as specified by a .csv file."""

# Based on this awesome example:
# http://stackoverflow.com/questions/22342097/is-it-possible-to-create-a-google-map-from-python

import csv
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
        reader = csv.reader(f)
        for row in reader:
            place_column = row[0]
            yield(place_column)


def get_geocoordinates_for_place(place):
    """Will return None if it can't resolve to coordinates."""
    try:
        return Geocoder.geocode(str(place)).coordinates
    except pygeolib.GeocoderError:
        print ("ERROR - Could not get coordinates for: " + str(place))
        return None


def visualize(csvfile):
    """Visualize places from .csv as google maps html page."""

    print("INFO - Reading file...")
    places = read_places_from_file(csvfile)
    unique_places = list(set(list(places)))
    sorted_places = sorted(unique_places)

    print("INFO - Querying coordinates...")
    points = []
    for place in sorted_places:
        point = get_geocoordinates_for_place(place)
        if point:
            points.append(point)

    print("INFO - Assembling map...")
    custom_map = Map()
    for point in points:
        custom_map.add_point(point)

    print("INFO - Writing results...")
    with open(DEFAULT_OUTPUTFILE, "w") as out:
        out.write(str(custom_map))

    print("INFO - Map written to " + DEFAULT_OUTPUTFILE)
    print("INFO - Open it in a web browser to see the map.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        print(USAGE)
    csvfile = args[0]
    visualize(csvfile)
