from time import mktime, time
from traceback import print_tb
import requests
import re
from datetime import date, datetime, time, timedelta

from headers import headers

from bs4 import BeautifulSoup, ResultSet

from consts import *
from utils import *

def meteogrGetCityName(soup):
    source_city = soup.find_all("h2", class_=re.compile("cityname flleft01"))
    source_city_list = filterResultSet2list(source_city, '>\w+[\s*\w+]*\s*</h2>', '>', ' </h2')
    return source_city_list[0]


def meteogrGetFirstHour(soup):
    source_hours = soup.find_all("td", class_= re.compile("innerTableCell fulltime"))
    
    starting_hour = filterResultSet2list(source_hours[0], '\d\d:\d\d', '', '')
    time_init = starting_hour[0] + ':00'
    time_init = datetime.strptime(time_init,"%X").time()

    return time_init

def meteogrGetAllTemperature(soup):
    source_celcius = soup.find_all("td", class_= re.compile("innerTableCell temperature"))
    
    source_celcius_list = filterResultSet2list(source_celcius, '>\d*<', '<', '>')
    
    return listStr2Flt(source_celcius_list)

def meteogrGetAllHumidity(soup):
    source_humidity = soup.find_all("td", class_= re.compile("innerTableCell hidden-xs"))

    source_humidity_list = filterResultSet2list(source_humidity, 'humidity\">\d*%<','humidity\">','%<')

    return listStr2Flt(source_humidity_list)

def meteogrGetAllWindSpeeds(soup):
    source_ws = soup.find_all("td", class_= re.compile("innerTableCell anemosfull"))
    
    source_ws_list = filterResultSet2list(source_ws, '\d* Km/h', '', 'Km/h')

    return listStr2Flt(source_ws_list)


def meteogrGetAllWindDirections(soup):
    source_wd = soup.find_all(
        "td", class_=re.compile("innerTableCell anemosfull"))

    source_wd_list = filterResultSet2list(
        source_wd, '\d* Bf \w*', '\d* Bf ', '')

    return source_wd_list


def meteogrGetAllSkyConditions(soup):
    source_skyCondition = soup.find_all(
        "td", class_=re.compile("innerTableCell PhenomenaSpecialTableCell phenomenafull"))
    source_skyCondition_list = filterResultSet2list(
        source_skyCondition, '"phenomeno-name" style="text-transform: uppercase" width="80%">\w*[\s\w*]*', '\"phenomeno-name\" style=\"text-transform: uppercase\" width=\"80%\">', '')
    
    return source_skyCondition_list


def meteogrGetTuple(url):
    page = requests.get(url, headers)
    
    if page.status_code==200:
        print('Success!')

    soup = BeautifulSoup(page.content, 'html.parser')

    # Get city name
    location = meteogrGetCityName(soup)
    print('Location: ', location)

    # Get humidity from meteo.gr
    humidity = meteogrGetAllHumidity(soup)

    # Get temperature from meteo.gr
    temp = meteogrGetAllTemperature(soup)

    # Get starting time
    time_init = meteogrGetFirstHour(soup)

    # Get wind speed from meteo.gr
    ws = meteogrGetAllWindSpeeds(soup)

    # Get wind direction from meteo.gr
    wd = meteogrGetAllWindDirections(soup)

    # Get sky conditions
    skyCondition = meteogrGetAllSkyConditions(soup)

    # Compute time interval
    date_init = date.today()
    if (time_init.strftime('%H:%M') == '00:00') & (datetime.now().strftime("%H:%M") < '23:59'):
        date_init = date_init + timedelta(days=1)
    print(date_init.strftime('%d/%m/%Y'))
    
    hours=[]
    time = datetime.combine(date_init, time_init)
    time_change = timedelta(hours=METEOGR_TIME_PERIOD_HOURS)
    for i in range(len(temp)):
        hours.append(time)
        time = time + time_change

    ### *** DEBUG ***
    # print('Temperatures')
    # for row in temp:
    #     print(row)

    # print('Humidity ')
    # for row in humidity:
    #     print(row)
    
    # print('Hours ')
    # for row in hours:
    #     print(row)

    # print('Windspeed')
    # for row in ws:
    #     print(row)

    # print("\n")
    # print(len(hours))
    # print(len(temp))
    # print(len(humidity))
    # print(len(ws))

    return location, hours, temp, humidity, ws, wd, skyCondition


def meteogrJoinTuple(url):
    location, hours, temp, humidity, ws, wd, skyCondition = meteogrGetTuple(url)
    
    hours_new_format = []
    for hour in hours:
        hours_new_format.append(hour.strftime(METEOGR_DAYTIME_FORMAT_CSV))

    joined_data = list(zip(hours_new_format,
                       temp, humidity, ws, wd, skyCondition))
    
    return joined_data, location

def meteogrPrintAllData(url):
    joined_data, location = meteogrJoinTuple(url)
    for data in joined_data:
        print(data)


def meteogrSaveAllDataCSV(url, filename=''):
    joined_data, location = meteogrJoinTuple(url)
    if not filename:
        filename = location + '_' + datetime.now().strftime(METEOGR_DAYTIME_FORMAT_FNAME) + '.csv'

    field_names = ['Date - Time', 'Temperature °C',
                   'Humidity %', 'Wind speed', 'Wind direction', 'Sky conditions']
    list2CSV(field_names, joined_data, filename)

def meteogrPlotTemperature(temp, hours, location=''):
    plot2D(hours, temp, 'date (Y-M-D)',
       'temperature  °C', location)


def meteogrPlotHumidity(humidity, hours, location=''):
    plot2D(hours, humidity,
           'date (Y-M-D)', 'humidity %', location)


def meteogrPlotWindSpeed(ws, hours, location=''):
    plot2D(hours, ws, 'date (Y-M-D)', 'wind speed Km/h', location)


def meteogrPlotWindrose(ws, wd):
    plotWindrose(ws, wd)


def meteogrPlotTuple(location, hours, temp, humidity, ws, wd):
    meteogrPlotTemperature(temp, hours, location)
    meteogrPlotHumidity(humidity, hours, location)
    meteogrPlotWindrose(ws, wd)
