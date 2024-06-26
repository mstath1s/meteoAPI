from time import mktime, time
from traceback import print_tb
from click import style
from numpy import source
import requests
import re
from datetime import date, datetime, time, timedelta

from headers import headers

from bs4 import BeautifulSoup, ResultSet

from consts import *
from meteogrAPI import meteogrGetAllWindDirections
from utils import *


def weathercomGetCityName(soup):
    source_city = soup.find_all(
        'span', class_='LocationPageTitle--PresentationName--1QYny')
    source_city_list = filterResultSet2list(
        source_city, '<span class="LocationPageTitle--PresentationName--1QYny" data-testid="PresentationName">\w+[\s*\w*]*', '<span class="LocationPageTitle--PresentationName--1QYny" data-testid="PresentationName">', '')

    return source_city_list[0]


def weathercomGetCurrentDate(soup):
    date = soup.find_all('h2', id=re.compile("currentDateId0"))

    # print(date)

    date = filterResultSet2list(date, '<h2 class="HourlyForecast--longDate--1tdaJ" id="currentDateId0">\w+, \w+ \d+</h2>',
                                 '<h2 class="HourlyForecast--longDate--1tdaJ" id="currentDateId0">\w+,\s*', '<[/]*h2>')
    
    date = datetime.strptime(str(date[0]), '%B %d')

    date = date.replace(year=date.today().year)

    print(date.date())

    return date.date()

def weathercomGetAllHours(soup):
    date_init = weathercomGetCurrentDate(soup)
    time_init = soup.find('h3', class_='DetailsSummary--daypartName--2FBp2')
    time_init = re.search('\d* [a|p]m', str(time_init)).group(0)

    if time_init:
        time_init = datetime.strptime(time_init, '%I %p')

    time_change = timedelta(hours=WEATHERCOM_TIME_PERIOD_HOURS)

    time = []
    time_init = datetime.combine(date_init, time_init.time())

    for hour in soup.find_all(
            'h3', class_='DetailsSummary--daypartName--2FBp2'):
        tmp = re.search('\d* [a|p]m', str(hour))
        if tmp:
            time.append(time_init)
            time_init = time_init + time_change

    return time


def weathercomGetAllTemperature(soup):
    source_celcius = soup.find_all(
        "span", class_=re.compile('DetailsSummary--tempValue--1K4ka'))

    source_celcius_list = filterResultSet2list(
        source_celcius, '<span class="DetailsSummary--tempValue--1K4ka" data-testid="TemperatureValue">\d+°</span>', '<span class="DetailsSummary--tempValue--1K4ka" data-testid="TemperatureValue">', '°</span>')

    temp = []

    for t in source_celcius_list:
        if WEATHERCOM_UNITS_USA == 1:
            temp.append(F2C(int(t)))
        else:
            temp.append(int(t))

    return temp


def weathercomGetAllHumidity(soup):
    source_humidity = soup.find_all(
        "div", class_=re.compile("DetailsTable--field--3ZKJV"))

    source_humidity_list = filterResultSet2list(
        source_humidity, 
        'data-testid="HumidityTitle">Humidity</span><span class="DetailsTable--value--1q_qD" data-testid="PercentageValue">\d+%</span></div>',
        'data-testid="HumidityTitle">Humidity</span><span class="DetailsTable--value--1q_qD" data-testid="PercentageValue">',
        '%</span></div>')

    # remove zeros
    source_humidity_list = [
        item for item in source_humidity_list if item != 0]

    # print(source_humidity_list)

    return listStr2Flt(source_humidity_list)


def weathercomGetAllSkyConditions(soup):
    source_skyCondition = soup.find_all(
        "span", class_=re.compile("DetailsSummary--extendedData--365A_"))
    source_skyCondition_list = filterResultSet2list(
        source_skyCondition, '<span class="DetailsSummary--extendedData--365A_">\w+[\s*\w+]*|[/w+]*</span>', '<span class="DetailsSummary--extendedData--365A_">', '</span>')
    # print(source_skyCondition_list)

    return source_skyCondition_list


def wethercomGetCloudCover(soup):
    source_cloudCover = soup.find_all(
        "li", class_=re.compile("DetailsTable--listItem--2yVyz"))
    # print(source_cloudCover)
    source_cloudCover_list = filterResultSet2list(
        source_cloudCover, 
        '<span class="DetailsTable--label--3Va-t" data-testid="CloudCoverTitle">Cloud Cover</span><span class="DetailsTable--value--1q_qD" data-testid="PercentageValue">\d+%</span>', 
        '<span class="DetailsTable--label--3Va-t" data-testid="CloudCoverTitle">Cloud Cover</span><span class="DetailsTable--value--1q_qD" data-testid="PercentageValue">', 
        '%</span>')

    # Remove zeros
    source_cloudCover_list = [item for item in source_cloudCover_list if item != 0]

    # print(source_cloudCover_list)

    return source_cloudCover_list


def weathercomGetAllWindSpeeds(soup):
    source_ws = soup.find_all(
        "span", class_=re.compile("Wind--windWrapper--3aqXJ DetailsTable--value--1q_qD"))
    # print(source_ws)
    if WEATHERCOM_UNITS_USA:
        source_ws_list = filterResultSet2list(
            source_ws,
            '<!-- -->\d+ mph',
            '<!-- -->',
            ' mph')
        source_ws_int = []
        for item in source_ws_list:
            source_ws_int.append(round(mph2kmh(int(item))))
            
    else:
        source_ws_list = filterResultSet2list(
            source_ws,
            '<!-- -->\d+ km/h',
            '<!-- -->',
            ' km/h')
        source_ws_int = listStr2Int(source_ws_list)

    # print(source_ws_int)

    return source_ws_int


def weathercomGetAllWindDirections(soup):
    source_wd = soup.find_all(
        "span", class_=re.compile("Wind--windWrapper--3aqXJ DetailsTable--value--1q_qD"))

    source_wd_list = filterResultSet2list(
        source_wd,
        '\w+ <!-- -->\d+',
        '',
        ' <!-- -->\d+')
    
    # print(source_wd_list)

    return source_wd_list


def weathercomGetAllUvIndices(soup):
    source_uv = soup.find_all(
        "div", class_=re.compile("DetailsTable--field--3ZKJV"))

    # print(source_uv)

    source_uv_list = filterResultSet2list(
        source_uv,
        '<span class="DetailsTable--value--1q_qD" data-testid="UVIndexValue">\d+ of 10</span></div>',
        '<span class="DetailsTable--value--1q_qD" data-testid="UVIndexValue">',
        ' of 10</span></div>')
    
    # Remove zeros
    source_uv_list = [
        item for item in source_uv_list if item != 0]

    # print(source_uv_list)

    return listStr2Int(source_uv_list)


def weathercomGetAllRain(soup):
    source_rain = soup.find_all(
        "div", class_=re.compile("DetailsTable--field--3ZKJV"))
    # print(source_rain)
    if WEATHERCOM_UNITS_USA:
        source_rain_list = filterResultSet2list(
            source_rain,
            'data-testid="AccumulationValue">[0.]*\d+ in</span></div>',
            'data-testid="AccumulationValue">',
            ' in</span></div>')
        
        # Remove zeros
        source_rain_list = [
            item for item in source_rain_list if item != 0]
        
        source_rain_int = []
        for item in source_rain_list:
            source_rain_int.append(round(in2mm(float(item)), 5))

    else:
        source_rain_list = filterResultSet2list(
            source_rain,
            'data-testid="AccumulationValue">[0.]*\d+ \w*m</span></div>',
            'data-testid="AccumulationValue">',
            ' \w*m</span></div>')

        # Remove zeros
        source_rain_list = [
            item for item in source_rain_list if item != 0]

        source_rain_int = listStr2Flt(source_rain_list)

    # print(source_rain_int)

    return source_rain_int


def weathercomGetTuple(url):
    # check compatibility of url
    if re.match('https://weather.com/weather/hourbyhour/[a-zA-Z0-9_]*', str(url)):
        printSuccessMsg('Link:<'+url+'> is correct')
    else:
        printErrorMsg('Link:<'+url+'> is incorrect')
        exit()

    page = requests.get(url, headers)

    if page.status_code == 200:
        printSuccessMsg('Success!')

    soup = BeautifulSoup(page.content, 'html.parser')

    # Get city name
    location = weathercomGetCityName(soup)
    print('Location: ', location)

    time = weathercomGetAllHours(soup)

    temp = weathercomGetAllTemperature(soup)
    
    humidity = weathercomGetAllHumidity(soup)

    skyCondition = weathercomGetAllSkyConditions(soup)

    source_cloudCover = wethercomGetCloudCover(soup)

    ws = weathercomGetAllWindSpeeds(soup)

    wd = weathercomGetAllWindDirections(soup)

    uv_idx = weathercomGetAllUvIndices(soup)

    rain_amount = weathercomGetAllRain(soup)

    return location, time, temp, humidity, ws, wd, skyCondition, source_cloudCover, uv_idx, rain_amount


def weathercomJoinTuple(url):
    location, time, temp, humidity, ws, wd, skyCondition, source_cloudCover, uv_idx, rain_amount = weathercomGetTuple(
        url)

    hours_new_format = []
    for hour in time:
        hours_new_format.append(hour.strftime(WEATHERCOM_DAYTIME_FORMAT_CSV))

    joined_data = list(zip(hours_new_format,
                       temp, humidity, ws, wd, skyCondition, source_cloudCover, uv_idx, rain_amount))

    return joined_data, location


def weathercomPrintAllData(url):
    joined_data, location = weathercomJoinTuple(url)
    for data in joined_data:
        print(data)


def weathercomSaveAllDataCSV(url, filename=''):
    joined_data, location = weathercomJoinTuple(url)
    if not filename:
        filename = location + '_' + \
            datetime.now().strftime(WEATHERCOM_DAYTIME_FORMAT_FNAME) + '.csv'

    if WEATHERCOM_UNITS_USA:
        field_names = ['Date - Time', 'Temperature (°F)',
                       'Humidity (%)', 'Wind speed (mph)', 'Wind direction', 'Sky conditions', 'Cloud Cover (%)', 'UV Index (/10)', 'Rain Amount (in)']
    else:
        field_names = ['Date - Time', 'Temperature (°C)',
                   'Humidity (%)', 'Wind speed (km/h)', 'Wind direction', 'Sky conditions', 'Cloud Cover (%)', 'UV Index (/10)', 'Rain Amount (mm)']
    list2CSV(field_names, joined_data, filename)


def weathercomPlotTemperature(temp, hours, location='', savefig=False, filename=''):
    if savefig == True:
        if filename == '':
            filename = location + '_temp' + '.png'

    plot2D(hours, temp, 'datetime (M-D H)',
           'temperature  °C', location, timedelta(hours=WEATHERCOM_TIME_PERIOD_HOURS), WEATHERCOM_DAYTIME_FORMAT_FIG, savefig, filename)


def weathercomPlotHumidity(humidity, hours, location='', savefig=False, filename=''):
    if savefig == True:
        if filename == '':
            filename = location + '_humidity' + '.png'
    
    plot2D(hours, humidity,
                 'datetime (M-D H)', 'humidity %', location, timedelta(hours=WEATHERCOM_TIME_PERIOD_HOURS), WEATHERCOM_DAYTIME_FORMAT_FIG, savefig, filename)


def weathercomPlotWindSpeed(ws, hours, location='', savefig=False, filename=''):
    if savefig == True:
        if filename == '':
            filename = location + '_windspeed' + '.png'
    
    plot2D(hours, ws, 
                'datetime (M-D H)', 'wind speed Km/h', location, timedelta(hours=WEATHERCOM_TIME_PERIOD_HOURS), WEATHERCOM_DAYTIME_FORMAT_FIG, savefig, filename)


def weathercomPlotWindrose(ws, wd, location='', savefig=False, filename=''):
    if savefig == True:
        if filename == '':
            filename = location + '_winddirection' + '.png'

    plotWindrose(ws, wd, savefig, filename)


def weathercomPlotUVIndex(uv_idx, hours, location='', savefig=False, filename=''):
    if savefig == True:
        if filename == '':
            filename = location + '_uvidx' + '.png'

    plot2D(hours, uv_idx, 'datetime (M-D H)', 'UV index',
          location, timedelta(hours=WEATHERCOM_TIME_PERIOD_HOURS), WEATHERCOM_DAYTIME_FORMAT_FIG, savefig, filename)

def weathercomPlotTuple(location, hours, temp, humidity, ws, wd, uv_idx, savefig=False):
    weathercomPlotTemperature(temp, hours, location, savefig)
    weathercomPlotHumidity(humidity, hours, location, savefig)
    weathercomPlotWindrose(ws, wd, location, savefig)
    weathercomPlotUVIndex(uv_idx, hours, location, savefig)


def weathercomPlotTupleAndSaveFigure(location, hours, temp, humidity, ws, wd, uv_idx):
    weathercomPlotTuple(location, hours, temp, humidity,
                        ws, wd, uv_idx, True)
