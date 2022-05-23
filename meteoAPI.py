import requests
import re

from headers import headers

from bs4 import BeautifulSoup, ResultSet

def filterResultSet2list(input, keep, remove_l='', remove_r=''):
    list=[]
    for item in input:
        filtered = re.search(keep, str(item))
        if filtered:
            filtered = filtered.group(0)
            filtered = filtered.replace(remove_l,'')
            filtered = filtered.replace(remove_r,'')
            list.append(filtered)
    
    return list


def meteogrGetAllHumidity(soup):
    source_humidity = soup.find_all("td", class_= re.compile("humidity"))

    source_humidity_list = filterResultSet2list(source_humidity, '\d\d\d*')

    return source_humidity_list

def meteogrGetAllTemperature(soup):
    source_celcius = soup.find_all("td", class_= re.compile("innerTableCell temperature normal tempwidth"))
    
    source_celcius_list = filterResultSet2list(source_celcius, '>\d\d\d*<', '<', '>')
    
    return source_celcius_list

def meteogrGetAllHours(soup):
    source_hours = soup.find_all("td", class_= re.compile("innerTableCell fulltime"))
    
    source_hours_list = filterResultSet2list(source_hours, '\d\d:\d\d')
    
    return source_hours_list    

def meteogrGetAllWindspeeds(soup):
    source_ws = soup.find_all("span", class_= re.compile("kmh"))
    
    source_ws_list = filterResultSet2list(source_ws, '\d\d* Km/h', '', 'Km/h')

    return source_ws_list


def meteoGetTuple(url):
    page = requests.get(url, headers)
    
    print(page.status_code)

    soup = BeautifulSoup(page.content, 'html.parser')

    humidity = meteogrGetAllHumidity(soup)

    temp = meteogrGetAllTemperature(soup)

    hours = meteogrGetAllHours(soup)

    ws = meteogrGetAllWindspeeds(soup)

    joined_data = list(zip(hours, temp, humidity, ws))

    for data in joined_data:
        print(data)

    return joined_data