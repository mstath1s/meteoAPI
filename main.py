from meteoAPI import *

if __name__ == "__main__":
    ### *** TEST 1 ***
    url = 'https://www.meteo.gr/cf-en.cfm?city_id=310' # Markoupoulo, Attica
    
    location, hours, temp, humidity, ws, wd, skyCondition = meteogrGetTuple(url)
    
    # meteogrPlotTuple(location, hours, temp, humidity)

    meteogrPlotWindrose(ws, wd)

    ### *** TEST 2 ***
    url = 'https://www.meteo.gr/cf-en.cfm?city_id=191' # El. Venizelos, Athens airport

    location, hours, temp, humidity, ws, wd, skyCondition = meteogrGetTuple(url)

    meteogrPlotWindrose(ws, wd)

    # meteogrPlotTuple(location, hours, temp, humidity)

    ### *** TEST 3 ***
    url = 'https://www.meteo.gr/cf-en.cfm?city_id=20' # Santorini, Cyclades

    location, hours, temp, humidity, ws, wd, skyCondition = meteogrGetTuple(url)

    meteogrPlotWindrose(ws, wd)

    # meteogrPlotTuple(location, hours, temp, humidity)
