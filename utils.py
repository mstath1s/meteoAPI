from consts import *

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from windrose import WindroseAxes

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
