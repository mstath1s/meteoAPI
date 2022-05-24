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
            filtered = filtered.replace(remove_l,'')
            filtered = filtered.replace(remove_r,'')
            list.append(filtered)
        else:
            list.append(0)
    
    return list

def meteogrGetFirstHour(soup):
    source_hours = soup.find_all("td", class_= re.compile("innerTableCell fulltime"))
    
    starting_hour = filterResultSet2list(source_hours[0], '\d\d:\d\d', '', ':\d\d')
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

def meteogrGetAllWindspeeds(soup):
    source_ws = soup.find_all("td", class_= re.compile("innerTableCell anemosfull"))
    
    source_ws_list = filterResultSet2list(source_ws, '\d* Km/h', '', 'Km/h')

    return source_ws_list

def listStr2Flt(list_of_strings):
    list_of_float = []
    for item in list_of_strings:
        list_of_float.append(float(item))
    return list_of_float

def plot2D(x, y, xlabel='', ylabel=''):
    plt.plot(x, y)  # Plot some data on the axes.
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

def meteoGetTuple(url):
    page = requests.get(url, headers)
    
    print(page.status_code)

    soup = BeautifulSoup(page.content, 'html.parser')

    humidity = meteogrGetAllHumidity(soup)

    temp = meteogrGetAllTemperature(soup)

    time_init = meteogrGetFirstHour(soup)

    ws = meteogrGetAllWindspeeds(soup)

    hours=[]
    time = datetime.combine(date.today(), time_init)

    time_change = timedelta(hours=3)

    for i in range(len(temp)):
        hours.append(time)
        time = time + time_change

    ###
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

    joined_data = list(zip(hours, temp, humidity, ws))
    
    timex = []
    for hour in hours:
        timex.append(mktime(hour.timetuple()))
    
    plot2D(hours, listStr2Flt(temp), 'date (Y-M-D)', 'temperature  °C')
    plot2D(hours, listStr2Flt(humidity), 'date (Y-M-D)', 'humidity \%')

    for data in joined_data:
        print(data)

    return joined_data