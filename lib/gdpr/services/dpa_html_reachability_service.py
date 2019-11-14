import requests
from lxml import html
from lxml.etree import XPathEvalError
import json
import csv

REACHABILITY_FLAG_SENTINEL = -1
REACHABILITY_FLAG_FAILURE = 0
REACHABILITY_FLAG_SUCCESS = 1

def setup_xpath_samples(dpa):
    xpath_samples = []

    # (country_code, xpath, label)
    with open('./gdpr/assets/dpa-html-reachability.csv', newline='\n') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        next(csv_reader) # skip header
        for row in csv_reader:
            row = [cell.lstrip(' ') for cell in row]
            country_code = row[0]
            if dpa.country_code.lower() != country_code.lower():
                continue
            xpath_samples.append((row[0], row[1], row[2], REACHABILITY_FLAG_SENTINEL))

    return xpath_samples

def dpa_html_reachability_service(dpa): # cand = dpa
    reachability = []
    xpath_samples = setup_xpath_samples(dpa)

    source = dpa.sources[0]
    host = source['host']
    start_path = source['start_path']

    response = requests.get(host + start_path)
    tree = html.fromstring(response.content)

    for country_code, xpath, label, reachability_flag in xpath_samples:
        reachability_flag_ = reachability_flag
        try:
            elements = tree.xpath(xpath)
            reachability_flag_ = REACHABILITY_FLAG_SUCCESS if len(elements) > 0 else REACHABILITY_FLAG_FAILURE
        except XPathEvalError:
            reachability_flag_ = REACHABILITY_FLAG_FAILURE
        reachability.append((country_code, xpath, label, reachability_flag_))

    return reachability
