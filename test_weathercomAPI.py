from weathercomAPI import *

if __name__ == "__main__":
    ### *** TEST 1 ***
    # Markoupoulo, Attica, Greece
    url = 'https://weather.com/weather/hourbyhour/l/21e963c34293ccc9c399128b3c25d32afd754dec039c0376a7c974185584f29d#detailIndex4'

    location, time, temp, humidity, ws, wd, skyCondition, source_cloudCover, uv_idx, rain_amount = weathercomGetTuple(url)
    weathercomPlotTuple(location, time, temp, humidity, ws, wd)

    # weathercomSaveAllDataCSV(url)

    # Kaunas, Kaunas, Lithuania
    url = 'https://weather.com/weather/hourbyhour/l/c0ad3acc0ae559d552ded89fb4af50e09b2063ef1ffa2bb7305acf6083011ea4'

    weathercomSaveAllDataCSV(url)
