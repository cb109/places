places
~~~~~~

Visualize visited places using Google Maps.

What is this
------------

A simple commandline script to convert a list of city names to an html
page displaying them with Google Maps.

Installation
------------

You need Python and the **pygeocoder** library. Install it via:

    $ pip install -r requirements.txt

How to use
----------

Prepare a .csv file with a single column, where each row contains the name
of a place/city. An example could be this (when viewed in a text editor):

::

    London;
    Berlin;
    Tokyo;

Then execute the script like:

    $ python places.py <my-visited-places.csv>

You need to be connected to the internet for this, since the script will
basically ask the Google Maps API to find coordinates based on you input.

The html will be places in your current working directory as **map.html**.
Open it in a browser to display the map.

Credits
-------

I built this by simply extending the following example code:
http://stackoverflow.com/questions/22342097/is-it-possible-to-create-a-google-map-from-python
