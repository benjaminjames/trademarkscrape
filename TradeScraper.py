# -*- coding: utf-8 -*-
#scrapy crawl trademarks -o TM_SCRAPE_OUT.csv -t csv

import re
import os
import time
import random
import scrapy
import itertools
from scrapy.http import Request
from scrapy.selector import Selector

from datetime import date, timedelta
from datetime import datetime as dt
import datetime as DT

from selenium import webdriver
import requests


driver = webdriver.Firefox()


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
        anyDate = dt.strptime(anyDate, '%Y/%m/%d')
        convertedDate = dt.strftime(anyDate, '%Y/%m/%d')
        return convertedDate

    from_date = dt.strptime(from_date, '%m/%d/%Y')
    to_date = dt.strptime(to_date, '%m/%d/%Y')

    daygen = (from_date + timedelta(x) for x in xrange((to_date - from_date).days))

    dates = [ "%s/%s/%s" % (day.year, day.month, day.day ) for day in daygen ]
    dates = [ convert(x).replace('/','') for x in dates ]

    # Order from most to least recent
    dates.reverse()

    return dates


def tomorrow():
    gmt = time.gmtime()
    ts = time.strftime('%m/%d/%y-%H:%M:%S', gmt)
    dtime = dt.strptime(ts, '%m/%d/%y-%H:%M:%S')
    dtime = dtime - DT.timedelta(hours=7)
    dtime = dtime + DT.timedelta(days=1)
    zoneTime = dtime.strftime('%-m/%-d/%Y')
    return zoneTime


def daysAgo(numDays):
    gmt = time.gmtime()
    ts = time.strftime('%m/%d/%y-%H:%M:%S', gmt)
    dtime = dt.strptime(ts, '%m/%d/%y-%H:%M:%S')
    dtime = dtime - DT.timedelta(hours=7)
    dtime = dtime - DT.timedelta(days=numDays)
    zoneTime = dtime.strftime('%-m/%-d/%Y')
    return zoneTime


### END HELPERS ###


def run(outputfilepath):

    '''
    Pick up where scraper left off based on record number
    CAVEAT: record number is based on one search query
    TODO: base record retrieval on serial number
    '''

    dates_to_scrape = generate_dates( daysAgo(30) , tomorrow() )

    scraped_record_filenames = flatten([x for x in os.walk(outputfilepath)][0])

    # TODO: Account for incomplete scraped days
    existing_dates_scraped = [ x.split('_')[0] for x in scraped_record_filenames if 'html' in x]

    dates_to_scrape = [d for d in dates_to_scrape if d not in existing_dates_scraped]

    print 'STARTING AT DATE: %s' % dates_to_scrape[0]

    find = driver.find_element_by_xpath

    # Get start page
    driver.get(start_page)

    # Navigate to TESS Trademark Search:
    find( TESS_TM_search ).click()
    time.sleep(4)

    # Navigate to Free Form Search
    find( free_form_search ).click()
    time.sleep(2)

    for filing_date in dates_to_scrape:

        search_string = '(live)[LD] and %s[FD]' % filing_date

        # Fill out search box and submit query
        find( free_form_search_box ).send_keys( search_string )

        find( submit_query ).click()

        time.sleep(2)

        try:
            records_for_filing_date = int( selextract( driver.page_source, total_records_xpath ) )
        except:
            records_for_filing_date = 0

        # From search results page, click on a result in order to see jump box
        try:
            find( search_results ).click()
            proceed = True
        except:
            proceed = False

        if proceed:

            time.sleep(2)

            # Crawl each TM using "Jump to record"
            for record_num in range( 1, records_for_filing_date+1 ):

                time.sleep(2)
                #persist_session()

                find( jump_box ).send_keys(record_num)
                find( jump_button ).click()

                # Capture whole pagetext and write to file:
                save_filename = '%s_%s' % (filing_date, str(record_num).zfill(5))

                page_content = driver.page_source

                f = open(outputfilepath + "%s.html" % (save_filename),'w')

                try:
                    f.write( page_content )
                except:
                    f.write( clean(page_content) )

                f.close()

                print "SCRAPED: %s of %s for %s" % (record_num,records_for_filing_date,filing_date)

            find( free_form_search_button ).click()
            find( clear_query ).click()

        else:
            driver.back()
            find( clear_query ).click()



            time.sleep(3)


# Send user-agent
# scrape_this = sesh.get(driver.current_url,headers={"user-agent":"Mozilla/5.0"}).content.lower()

run('all_tm_records/')

driver.close()
