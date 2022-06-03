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
    for hour in soup.find_all(
            'h3', class_='DetailsSummary--daypartName--2FBp2'):
        tmp = re.search('\d* [a|p]m', str(hour))
        if tmp:
            tmp = datetime.combine(date_init, time_init.time())
            time_init = time_init + time_change

            time.append(tmp)

    return time


def weathercomGetAllTemperature(soup):
    source_celcius = soup.find_all(
        "span", class_=re.compile('DetailsSummary--tempValue--1K4ka'))

    source_celcius_list = filterResultSet2list(
        source_celcius, '<span class="DetailsSummary--tempValue--1K4ka" data-testid="TemperatureValue">\d+°</span>', '<span class="DetailsSummary--tempValue--1K4ka" data-testid="TemperatureValue">', '°</span>')

    temp = []

    for t in source_celcius_list:
        if WEATHERCOM_TEMP_UNIT_C != 1:
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

    print(source_humidity_list)

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

def weathercomGetTuple(url):
    page = requests.get(url, headers)

    if page.status_code == 200:
        print('Success!')

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
