


# -*- coding: utf-8 -*-

import time
import scrapy
import requests
import itertools
import csvmodule as cs

from datetime import datetime
from scrapy.selector import Selector

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


def select(text,xpath):
    SelectX = Selector(text=text).xpath
    return SelectX(xpath).extract()

def selextract(xpath):
    SelectX = Selector(text=driver.page_source).xpath
    return SelectX(xpath).extract_first()

def clickon(xpath):
    try:
        element = driver.find_element_by_xpath(xpath)
    except:
        print "RETRYING CLICKON() for %s" % (xpath)
        time.sleep(1)
        clickon(xpath)
    else:
        element.click()
        time.sleep(2)

fields = {
'brand' : './/*[@id="%s"]//*[@aria-describedby="gridForsearch_pane_BRAND"]/text()',
'source' : './/*[@id="%s"]//*[@aria-describedby="gridForsearch_pane_SOURCE"]/text()',
'status' : './/*[@id="%s"]//*[@aria-describedby="gridForsearch_pane_STATUS"]/text()',
'origin' : './/*[@id="%s"]//*[@aria-describedby="gridForsearch_pane_OO"]/text()',
'holder' : './/*[@id="%s"]//*[@aria-describedby="gridForsearch_pane_HOL"]/text()',
'number' : './/*[@id="%s"]//*[@aria-describedby="gridForsearch_pane_ID"]/text()',
'reg_date' : './/*[@id="%s"]//*[@aria-describedby="gridForsearch_pane_RD"]/text()',
'app_date' : './/*[@id="%s"]//*[@aria-describedby="gridForsearch_pane_AD"]/text()'
}


hover_xpath = '//*[@class="qtip qtip-default  qtip-pos-bl"]'
next_button = '//*[@class="ui-button-icon-primary ui-icon ui-icon-triangle-1-e"]'

url = "http://www.wipo.int/branddb/en/?q={'searches':[{'te':'mobile application','fi':'GS_ALL','df':'GS'}]}&sep=;#"
url = 'http://www.wipo.int/branddb/en/?q={"searches":[{"te":"king.com","fi":"HOL"}]}'

driver = webdriver.Firefox()
driver.get(url)
time.sleep(12)

while True:
    count = 1
    f = open("WIPO DATA/MOBILE GAME TRADEMARKS_PAGE_%s.html" % count,'w')
    f.write(driver.page_source.encode('ascii','ignore'))
    f.close()
    '''
    results = []
    # Get each record from page
    for num in range(30):
        record = {}
        for field in fields:
            field_xpath = fields[field] % num
            record[field] = selextract(field_xpath).encode('ascii','ignore')
        results.append(record)
        cs.write("TM TEST",results)
    '''
    next_field = driver.find_element_by_xpath(hover_xpath)
    Hover = ActionChains(driver).move_to_element(next_field).move_to_element(next_button)
    Hover.click().build().perform()

    clickon(next_button)
    time.sleep(4)
    count += 1
