# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import traceback
import itertools
from scrapy.http import Request
from scrapy.selector import Selector

from datetime import date, timedelta
from datetime import datetime as dt
import datetime as DT

from selenium import webdriver
import requests

import mlab as mlab


start_page = "http://www.uspto.gov/trademarks-application-process/search-trademark-database"
TESS_TM_search = "/html/body/div[1]/main/div/div/div[2]/div[3]/article/div/div/p[3]/a"
free_form_search = "html/body/center/table[1]/tbody/tr[4]/td/font/font/a"
submit_query = "html/body/form/b/b/table[2]/tbody/tr[1]/td/input[1]"
free_form_search_box = ".//*[@name='p_s_ALL']"
search_results = "html/body/table[7]/tbody/tr[2]/td[4]/a"
jump_box = "html/body/table[4]/tbody/tr/td[5]/input"
jump_button = "html/body/table[4]/tbody/tr/td[4]/form/input[3]"
free_form_search_button = '/html/body/a[4]/img'
clear_query = '/html/body/form/b/b/table[2]/tbody/tr[1]/td/input[2]'
total_records_xpath = '/html/body/table[4]/tbody/tr/td[6]/font/text()'



### HELPERS ###


def flatten(list_of_lists):
    # import itertools
    return list(itertools.chain(*list_of_lists))


def clean(anystring):
	return re.sub(r'[^\x00-\x7f]',r'',anystring)


def persist_session():
    # Set cookies to persist session:
    cookies = driver.get_cookies()
    sesh = requests.Session()
    for cookie in cookies:
        sesh.cookies.set(cookie['name'], cookie['value'])


def selextract(page_text,xpath):
    # Extracts data from HTML
    SelectX = Selector(text=page_text).xpath
    data = SelectX(xpath).extract_first()

    return data


def generate_dates(from_date, to_date):
    '''
    Generates list of daily dates up to BUT NOT including to_date
    ex: generate_dates('4/1/2017','4/11/2017')
    '''

    def convert(anyDate):
        anyDate = dt.strptime(anyDate, '%Y-%m-%d')
        convertedDate = dt.strftime(anyDate, '%Y-%m-%d')
        return convertedDate

    from_date = dt.strptime(from_date, '%m-%d-%Y')
    to_date = dt.strptime(to_date, '%m-%d-%Y')

    daygen = (from_date + timedelta(x) for x in xrange((to_date - from_date).days))

    dates = [ "%s-%s-%s" % (day.year, day.month, day.day ) for day in daygen ]

    dates = [ convert(x) for x in dates ]

    # Order from most to least recent
    dates.reverse()

    return dates


def tomorrow():
    gmt = time.gmtime()
    ts = time.strftime('%m/%d/%y-%H:%M:%S', gmt)
    dtime = dt.strptime(ts, '%m/%d/%y-%H:%M:%S')
    dtime = dtime - DT.timedelta(hours=7)
    dtime = dtime + DT.timedelta(days=1)
    zoneTime = dtime.strftime('%-m-%-d-%Y')
    return zoneTime


def daysAgo(numDays):
    gmt = time.gmtime()
    ts = time.strftime('%m/%d/%y-%H:%M:%S', gmt)
    dtime = dt.strptime(ts, '%m/%d/%y-%H:%M:%S')
    dtime = dtime - DT.timedelta(hours=7)
    dtime = dtime - DT.timedelta(days=numDays)
    zoneTime = dtime.strftime('%-m-%-d-%Y')
    return zoneTime


def getMostRecentDate(listOfDates):
    dtimes = {dt.strptime(x, '%Y-%m-%d') - dt(1970, 1, 1): x for x in listOfDates}
    epochs = {k.total_seconds(): v for k, v in dtimes.items()}
    recentEpoch = max(epochs.keys())
    mostRecent = epochs[recentEpoch]
    return mostRecent


# Print iterations progress
def print_progress(process_name, iteration, total):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    prefix = 'Progress'
    suffix = 'Complete'

    decimals = 1
    bar_length = 100
    iteration = iteration + 1

    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (process_name, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


### END HELPERS ###
