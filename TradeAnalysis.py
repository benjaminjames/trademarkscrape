
import re
import time
import requests
import csvmodule as cs
from collections import OrderedDict


def solr_score(wordmark):
    wordmark = wordmark.lower().strip().replace(" ",'+')
    print "Searching %s" % wordmark
    # Gets fuzzy result count from Solr (main core only)
    solr_search = ('http://solrcluster-1910154206.us-east-1.elb.amazonaws.com/solr/app_searchb/focusip2?q=status%3A%22A%22+AND+appTitle%3A%22'+wordmark+'%22%0A&rows=1&fl=appTitle&wt=json&indent=true')
    solr_req = requests.get(solr_search)
    solr_json = solr_req.json()
    solr_score = solr_json['response']['numFound']

    print "%s // %s" % (wordmark,solr_score)
    return solr_score

tm_data = cs.get("ALL_TRADEMARKS_FULL")
unique_applicants = list(set([x['(applicant)'] for x in tm_data]))

for tm in tm_data:
    tm['solr_score'] = solr_score(tm['word mark'])

results = []
for applicant in unique_applicants:
    metrics = OrderedDict()
    # grab all records specific to each applicant
    applicant_tms = [x for x in tm_data if x['(applicant)'] == applicant]
    # run analysis
    metrics['owner'] = applicant
    metrics['owner_wordmarks'] = \
        " // ".join([x['word mark'] for x in tm_data if x['(applicant)'] == applicant])
    metrics['num_trademarks'] = len(applicant_tms)
    metrics['solr_exact_score'] = sum([int(x['solr_score_exact']) for x in applicant_tms])
    metrics['solr_score'] = sum([int(x['solr_score']) for x in applicant_tms])
    # write csv
    results.append(metrics)
    cs.write("TM_Analysis",results)
