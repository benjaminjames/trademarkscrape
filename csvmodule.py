import os
import csv
import json
from collections import OrderedDict
from xlsxwriter import Workbook

'''
Makes CSV stuff easy.
'''


# Ingest CSV / return a list of dictionaries
def get(filename):
    data = []
    if '.csv' in filename:
        with open(filename, 'U') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data
    else:
        with open(filename + '.csv', 'U') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data


# Take 'data' (list of dicts / single dict / string) and write to CSV:
def write(filename, data):  # mode = 'w' most common
    with open(filename + '.csv', 'w') as output_file:
        if type(data) is list:

            # ENCODE AS ASCII
            for d in data:
                for k, v in d.items():
                    if type(v) != int:
                        try:
                            d[k] = v.encode('ascii', 'ignore')
                        except:
                            d[k] = v

            # GET ALL KEYS FROM LIST OF DICTS (SOME DICTS MAY HAVE DIFF KEYS)
            keys = list(set().union(*(d.keys() for d in data)))

            # WRITE TO FILE
            writer = csv.DictWriter(output_file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

        elif type(data) is dict or type(data) is OrderedDict:
            fieldnames = data.keys()
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)

        elif type(data) is str or unicode:
            output_file.write(data + '\n')

        else:
            print "--Unsupported data type for csvmodule.write()--"


# Take 'data' (list of dicts / single dict / string) and write to CSV:
def append(filename, data):  # mode = 'w' most common
    with open(filename + '.csv', 'a') as output_file:
        if type(data) is list:
            # GET ALL KEYS FROM LIST OF DICTS (SOME DICTS MAY HAVE DIFF KEYS)
            keys = list(set().union(*(d.keys() for d in data)))
            # WRITE TO FILE
            writer = csv.DictWriter(output_file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        elif type(data) is dict or type(data) is OrderedDict:
            fieldnames = data.keys()
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)
        elif type(data) is str or unicode:
            output_file.write(data + '\n')
        else:
            print "--Unsupported data type--"


def write_to_excel(filename, list_of_dicts):
    filename = filename + '.xlsx'
    ordered_list = list(set().union(*(d.keys() for d in list_of_dicts)))
    # setup
    wb = Workbook(filename)
    ws = wb.add_worksheet("Sheet 1")  # or leave it blank, default name is "Sheet 1"
    # set start
    first_row = 0
    for header in ordered_list:
        col = ordered_list.index(header)  # we are keeping order.
        ws.write(first_row, col, header)  # we have written first row which is the header of worksheet also.
    # do magic
    row = 1
    for each_dict in list_of_dicts:
        for _key, _value in each_dict.items():
            col = ordered_list.index(_key)
            ws.write(row, col, unicode(_value))
        row += 1  # enter the next row
    wb.close()


def get_filenames(path):
    # print "PICKING UP FILENAMES FROM %s" % path
    filenames = []
    for root, dirs, files in os.walk(path):
        for fname in files:
            if '.DS' not in fname:
                filenames.append(fname)
    return filenames


def get_all_csvs_in_dir(dirname):
    # Fetches data from all CSV's present in the given directory
    dirname = dirname + '/'
    results = []

    for root, dirs, files in os.walk(dirname):
        for index, filename in enumerate(files):
            if '_store' not in filename.lower():
                print "GETTING DATA FROM %s" % filename
                data = get(dirname + filename.replace('.csv', ""))
                results += data

    return results


def load_json(filename):
    if '.json' in filename:
        loaded = json.loads(open(filename, 'rb').read())
    else:
        loaded = json.loads(open(filename + '.json', 'rb').read())
    return loaded
