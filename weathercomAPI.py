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
    print(temp)
