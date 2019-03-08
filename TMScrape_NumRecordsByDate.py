# -*- coding: utf-8 -*-


#TODO: refactor to only retrieve WORD MARKS


from TMScrape_helpers import *


driver = webdriver.PhantomJS()



def main():

    destination = mlab.get_collection('app_data','tm_record_dates',True)

    existing_records = destination.distinct('TM RECORD DATE')

    dates_to_scrape = generate_dates( daysAgo(2090) , tomorrow() )

    dates_to_scrape = [d for d in dates_to_scrape if d not in existing_records]


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

    joblen = len(dates_to_scrape)

    for count, filing_date in enumerate(dates_to_scrape):

        print_progress('TM RECORDS BY DATE',count,joblen)

        fdate = filing_date.replace('-','')

        result = {}
        result['TM RECORD DATE'] = filing_date
        result['LOCKED'] = False
        result['ALL RECORDS SCRAPED'] = False

        search_string = '(live)[LD] and %s[FD]' % fdate

        # Fill out search box and submit query
        find( free_form_search_box ).send_keys( search_string )
        find( submit_query ).click()

        time.sleep(1)

        try:
            records_for_filing_date = int( selextract( driver.page_source, total_records_xpath ) )
        except:
            records_for_filing_date = 0


        if records_for_filing_date != 0:

            result['TM RECORDS FOR FILING DATE'] = records_for_filing_date

            destination.insert( result )


        driver.back()
        find( clear_query ).click()


# Send user-agent
# scrape_this = sesh.get(driver.current_url,headers={"user-agent":"Mozilla/5.0"}).content.lower()

main()

driver.close()
