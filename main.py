import requests
import re
from meteoAPI import *

from bs4 import BeautifulSoup, ResultSet

if __name__ == "__main__":

    url = 'https://www.meteo.gr/cf-en.cfm?city_id=310'
    
    location, hours, temp, humidity, ws = meteogrGetTuple(url)
    
    meteogrPlotTuple(location, hours, temp, humidity, ws)

    url = 'https://www.meteo.gr/cf-en.cfm?city_id=191'

    location, hours, temp, humidity, ws = meteogrGetTuple(url)

    meteogrPlotTuple(location, hours, temp, humidity, ws)
