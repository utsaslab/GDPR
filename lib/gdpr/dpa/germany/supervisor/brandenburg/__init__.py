import os
import math
import requests
import json
import datetime
import hashlib
import dateparser
import re
import csv

from ... import DPA

from bs4 import BeautifulSoup

from .....services.links_from_soup_service import links_from_soup_service
from .....services.filename_from_path_service import filename_from_path_service
from .....services.pdf_to_text_service import pdf_to_text_service

from .....specifications import pdf_file_extension_specification
from .....specifications import page_fully_rendered_specification
from .....specifications import gdpr_retention_specification

from .....modules.pagination import Pagination
from .....policies import bulk_collect_location_policy
from .....policies import gdpr_policy

import textract

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .....policies import webdriver_executable_path_policy

class Brandenburg(DPA):
    def __init__(self):
        iso_code='de'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = {
            "host": "https://www.lda.brandenburg.de",
            "start_path": "/cms/detail.php/bb1.c.233960.de/bbo_press"
        }

        host = source['host']
        start_path = source['start_path']

        language_code = 'de'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        source_url = host + start_path

        now = datetime.datetime.now()
        gdpr_date = gdpr_policy.implementation_date()
        year_range = range(gdpr_date.year, now.year + 1)

        pagination = Pagination()
        for year in year_range:
            pagination.add_item(source_url + f"?_year={year}&_cat=")

        while pagination.has_next():
            page_url = pagination.get_next()
            print('page_url:', page_url)

            results_response = requests.request('GET', page_url)
            results_content = results_response.content
            results_soup = BeautifulSoup(results_content, 'html.parser')

            content = results_soup.find('div', id='content')
            if content is None:
                return True

            for beitrag in content.find_all('div', class_='beitrag'):
                h3_all = beitrag.find_all('h3')
                p_all = beitrag.find_all('p')
                if len(h3_all) != len(p_all):
                    return True

                for i in range(len(h3_all)):
                    h3 = h3_all[i]
                    p = p_all[i]

                    span_date = h3.find('span', class_='date')
                    if span_date is None:
                        return True
                    date_str = span_date.get_text()
                    # ex: 18.10.2019
                    tmp = datetime.datetime.strptime(date_str, '%d.%m.%Y')
                    date = datetime.date(tmp.year, tmp.month, tmp.day)

                    if gdpr_retention_specification.is_satisfied_by(date) is False:
                        continue # try another result_link # should be continue

                    document_title = h3.get_text()
                    if document_title.startswith(date_str) is True:
                        document_title = document_title.replace(date_str, '').lstrip()

                    document_folder = document_title
                    document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                    print("\tdocument_hash:\t", document_folder_md5)

                    a = p.find('a')
                    if a is None:
                        return True

                    document_href = a.get('href')
                    document_url = host + document_href

                    try:
                        document_response = requests.request('GET', document_url)
                        document_content = document_response.content
                        document_soup = BeautifulSoup(document_content, 'html.parser')

                        dirpath = root_path + '/' + document_folder_md5
                        try:
                            os.makedirs(dirpath)

                            press = document_soup.find('div', id='press')
                            if press is None:
                                return True

                            document_text = press.get_text()
                            with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                                f.write(document_text)

                        except FileExistsError:
                            print('Directory path already exists, continue.')
                    except:
                        print('something went wrong getting the doc.')

        return True
