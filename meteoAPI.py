from time import mktime, time
import requests
import re
from datetime import date, datetime, time, timedelta

from headers import headers

from bs4 import BeautifulSoup, ResultSet

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def filterResultSet2list(input, keep, remove_l='', remove_r=''):
    list=[]
    for item in input:
        filtered = re.search(keep, str(item))
        if filtered:
            filtered = filtered.group(0)
            filtered = re.sub(remove_l, '', filtered)
            filtered = re.sub(remove_r, '', filtered)
            list.append(filtered)
        else:
            list.append(0)
    
    return list

def meteogrGetCityName(soup):
    source_city = soup.find_all("h2", class_=re.compile("cityname flleft01"))
    source_city_list = filterResultSet2list(source_city, '>\w+\s*</h2>', '>', ' </h2')
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
    
    return source_celcius_list

def meteogrGetAllHumidity(soup):
    source_humidity = soup.find_all("td", class_= re.compile("innerTableCell hidden-xs"))

    source_humidity_list = filterResultSet2list(source_humidity, 'humidity\">\d*%<','humidity\">','%<')

    return source_humidity_list

def meteogrGetAllWindSpeeds(soup):
    source_ws = soup.find_all("td", class_= re.compile("innerTableCell anemosfull"))
    
    source_ws_list = filterResultSet2list(source_ws, '\d* Km/h', '', 'Km/h')

    return source_ws_list


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

def listStr2Flt(list_of_strings):
    list_of_float = []
    for item in list_of_strings:
        list_of_float.append(float(item))
    return list_of_float

def plot2D(x, y, xlabel='', ylabel='', title=''):
    plt.plot(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()

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

    # Get windspeed from meteo.gr
    ws = meteogrGetAllWindSpeeds(soup)

    wd = meteogrGetAllWindDirections(soup)
    print(wd)

    # Get sky conditions
    skyCondition = meteogrGetAllSkyConditions(soup)

    # Compute time interval
    date_init = date.today()
    if time_init.strftime('%H:%M') > '21:00':
        date_init = date_init + timedelta(days=1)
    # print(date_init)
    
    hours=[]
    time = datetime.combine(date_init, time_init)
    time_change = timedelta(hours=3)
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

    return location, hours, temp, humidity, ws, skyCondition


def meteogrJoinTuple(url):
    hours, temp, humidity, ws, skyCondition = meteogrGetTuple(url)

    joined_data = list(zip(hours, temp, humidity, ws, skyCondition))

    # convert time to timestamp format
    # timex = []
    # for hour in hours:
    #     timex.append(mktime(hour.timetuple()))

    # for data in joined_data:
    #     print(data)

    return joined_data


def meteogrPlotTuple(location, hours, temp, humidity, ws):
    plot2D(hours, listStr2Flt(temp), 'date (Y-M-D)',
           'temperature  °C', location)
    plot2D(hours, listStr2Flt(humidity),
           'date (Y-M-D)', 'humidity %', location)
    plot2D(hours, listStr2Flt(ws), 'date (Y-M-D)', 'wind speed Km/h', location)
