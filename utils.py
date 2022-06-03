import re

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from windrose import WindroseAxes

from consts import *

import csv 

def filterResultSet2list(input, keep, remove_l='', remove_r=''):
    list = []
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


def listStr2Flt(list_of_strings):
    list_of_float = []
    for item in list_of_strings:
        list_of_float.append(float(item))
    return list_of_float

def listStr2Int(list_of_strings):
    list_of_int = []
    for item in list_of_strings:
        list_of_int.append(int(item))
    return list_of_int

def plot2D(x, y, xlabel='', ylabel='', title=''):
    plt.plot(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


def WindDirTxt2Deg(wd):
    wd_deg = []
    for wd_txt in wd:
        if wd_txt in WIND_DIRECTION:
            wd_deg.append(WIND_DIRECTION.index(wd_txt) * 22.5)
        else:
            wd_deg.append(0)

    return wd_deg

def plotWindrose(ws, wd):
    ws_flt = listStr2Flt(ws)
    wd_deg = WindDirTxt2Deg(wd)

    ax = WindroseAxes.from_ax()
    ax.bar(wd_deg, ws_flt, normed=True, opening=0.8, edgecolor='white')
    ax.set_legend()
    plt.show()


def list2CSV(field_names, input_list, filename='output'):
    with open(filename, 'w') as f:
        write = csv.writer(f)

        write.writerow(field_names)
        write.writerows(input_list)

def F2C(tempF):
    return round((tempF - 32) * 0.5555)

def mph2kmh(mph):
    return mph * 1.60934

def in2cm(inches):
    return inches * 2.54

def printErrorMsg(message):
    print('\x1b' + PRINT_ERROR_COLOR + message + '\x1b[0m')

def printSuccessMsg(message):
    print('\x1b' + PRINT_SUCCS_COLOR + message + '\x1b[0m')


# Test utils
if __name__ == "__main__":
    print(F2C(0))
    print(F2C(32))

    mph2kmh(1)

    in2cm(1)

    printErrorMsg('error')

    printSuccessMsg('success')
