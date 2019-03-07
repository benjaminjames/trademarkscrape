
import xmltodict
import collections
import csvmodule as cs
import requests, zipfile, StringIO

reed_index = "http://trademarks.reedtech.com/downloads/pairdownload/{}.zip" #APP_NUM
uspto_daily = "https://bulkdata.uspto.gov/data3/trademark/dailyxml/applications/apc151231-01.zip"

### HELPERS ###

def inspect_json(level,nested_json):
    for key in nested_json.keys():
        print "{}-{}".format((level)*'    ',key)
        if isinstance(nested_json[key],dict):
            inspect_json(level+1,nested_json[key])

def flatten_json(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

### END HELPERS ###

def download_zipfile(file_path,zip_file_url):
    # Extract .zip file from URL to file
    r = requests.get(zip_file_url, stream=True)
    z = zipfile.ZipFile(StringIO.StringIO(r.content))
    z.extractall(file_path)
    print "EXTRACTED %s" % zip_file_url.split('/')[-1]

def download_tm_xml_docs(file_path):
    reeds_url = "http://trademarks.reedtech.com/downloads/TrademarkAssignments/2017/{}.zip"
    uspto_url = "https://bulkdata.uspto.gov/data3/trademark/dailyxml/assignments/{}.zip"
    # TODO generate proper list of dates
    # Download TM assignment (.zipped XML) info for each day
    filenames = ['asb%s' % num for num in range(170220,170222)]
    urls = [uspto_url.format(fname) for fname in filenames]
    for url in urls:
        download_zipfile(file_path,url)

def dictify_tm_xml_docs(file_path):
    results = []
    for fname in cs.get_filenames_by_dirpath(file_path):
        print fname
        f = open(file_path+fname)
        # Parse the shit outta some shit
        data = xmltodict.parse(f.read())
        return data

def parse_tm_xml(file_path):
    results = []
    dictified_data = dictify_tm_xml_docs(file_path)
    tm_assigns = dictified_data['trademark-assignments']
    for doc in tm_assigns['assignment-information']['assignment-entry']:
        flat_doc = flatten_json(doc)
        clean_doc = {k:v.encode('ascii','ignore') for k,v in flat_doc.items() if type(v) != list}
        results.append(flat_doc)
        cs.write("USPTO TMs",'w',results)


download_tm_xml_docs('tm_records/')
parse_tm_xml('tm_records/')


### DATA DERIVED FROM http://trademarks.reedtech.com/tmassign.php ###
