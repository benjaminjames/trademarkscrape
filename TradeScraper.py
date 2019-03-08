# -*- coding: utf-8 -*-


from TMScrape_helpers import *


driver = webdriver.Firefox()


def main():

    '''
    Pick up where scraper left off based on record number
    CAVEAT: record number is based on one search query
    TODO: base record retrieval on serial number
    '''
    tm_record_dates_collection = mlab.get_collection('app_data','tm_record_dates',True)
    tm_collection = mlab.get_collection('app_data','trademarks',True)

    find = driver.find_element_by_xpath

    # Get start page
    driver.get(start_page)

    # Navigate to TESS Trademark Search:
    find( TESS_TM_search ).click()
    time.sleep(2)

    # Navigate to Free Form Search
    find( free_form_search ).click()
    time.sleep(2)

    incomplete_query = {
        'ALL RECORDS SCRAPED' : False,
        'LOCKED' : False,
        'TM RECORDS FOR FILING DATE' : { '$ne' : 0 }
        }

    lock = { '$set' : { 'LOCKED' : True } }
    unlock = { '$set' : { 'LOCKED' : False } }

    while True:

        try:

            # Get a date from tm_record_dates collection where ALL RECORDS SCRAPED == False
            unharvested_dates = tm_record_dates_collection.distinct('TM RECORD DATE', incomplete_query )

            most_recent_date = getMostRecentDate(unharvested_dates)

            print 'SCRAPING TM FOR: ', most_recent_date

            tm_date_record = tm_record_dates_collection.find_one( {'TM RECORD DATE' : most_recent_date } )

            tm_record_dates_collection.update( { '_id' : tm_date_record['_id'] } , lock )

            date_to_process = tm_date_record['TM RECORD DATE']
            num_records_to_process = int(tm_date_record['TM RECORDS FOR FILING DATE'])

            date_query = {'RECORD DATE' : date_to_process }

            record_nums_harvested_for_date = tm_collection.distinct('RECORD NUMBER',date_query)

            record_nums_to_get = [x for x in range(num_records_to_process + 1) if str(x) not in record_nums_harvested_for_date]

            # Navigate TESS to TM records
            filing_date_formatted = date_to_process.replace('-','')

            search_string = '(live)[LD] and %s[FD]' % filing_date_formatted

            # Fill out search box and submit query
            find( free_form_search_box ).send_keys( search_string )

            find( submit_query ).click()

            time.sleep(1)

            # From search results page, click on a result in order to see jump box

            find( search_results ).click()

            joblen = len(record_nums_to_get)

            for count,record_num in enumerate(record_nums_to_get):

                time.sleep(.5)

                print date_to_process
                print_progress('TM', count, joblen )

                # Crawl TM using "Jump to record"

                #persist_session()

                find( jump_box ).send_keys(record_num)
                find( jump_button ).click()

                # Capture whole pagetext and write to file:
                save_filename = '%s_%s' % ( date_to_process, record_num )

                page_content = driver.page_source

                f = open('tm_record_temp/' + "%s.html" % (save_filename),'w')

                try:
                    f.write( page_content )
                except:
                    f.write( clean(page_content) )

                f.close()

            complete = {'$set' : {'ALL RECORDS SCRAPED' : True } }

            tm_record_dates_collection.update( { '_id' : tm_date_record['_id'] } , complete )

            find( free_form_search_button ).click()
            find( clear_query ).click()

        except:

            print traceback.format_exc()

            tm_record_dates_collection.update( { '_id' : tm_date_record['_id'] } , unlock )

            driver.close()

            quit()



# Send user-agent
# scrape_this = sesh.get(driver.current_url,headers={"user-agent":"Mozilla/5.0"}).content.lower()

main()

driver.close()
