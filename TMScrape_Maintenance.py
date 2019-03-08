# -*- coding: utf-8 -*-

from TMScrape_helpers import *


# Update ALL RECORDS SCRAPED field based on number of records in collection

tm_collection = mlab.get_collection('app_data','trademarks',True)
tm_record_dates_collection = mlab.get_collection('app_data','tm_record_dates',True)


def updateCompletedScrapeDates():
    incomplete_query = {
        'ALL RECORDS SCRAPED' : False,
        'LOCKED' : False,
        'TM RECORDS FOR FILING DATE' : { '$ne' : 0 }
        }

    check_records = tm_record_dates_collection.find( incomplete_query )

    for record in check_records:
        q = {'RECORD DATE' : record['TM RECORD DATE'] }

        total_TMs_for_date = record['TM RECORDS FOR FILING DATE']

        num_TMs_harvested_for_date = tm_collection.count( q )

        print record['TM RECORD DATE'],total_TMs_for_date,num_TMs_harvested_for_date

        if num_TMs_harvested_for_date >= total_TMs_for_date:

            target = { 'TM RECORD DATE' : record['TM RECORD DATE'] }
            updater = {'$set' : {'ALL RECORDS SCRAPED' : True } }

            tm_record_dates_collection.update( target, updater )


def cleanOldDocs():

    q = mlab.fieldContains('RECORD NUMBER','html')

    proj = ['RECORD NUMBER','_id']

    docs = tm_collection.find( q ,projection=proj)

    joblen = tm_collection.count( q )

    count = 0

    for d in docs:
        print_progress('CLEAN',count,joblen)
        count += 1

        d['RECORD NUMBER'] = d['RECORD NUMBER'].strip('.html')

        target = {'_id' : d['_id'] }
        update = {'$set' : d }
        tm_collection.remove
        tm_collection.update( target, update )



#cleanOldDocs()
