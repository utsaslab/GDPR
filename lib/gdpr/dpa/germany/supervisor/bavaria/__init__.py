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

class Bavaria(DPA):
    def __init__(self):
        iso_code='de'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = {
            "host": "https://www.datenschutz-bayern.de",
            "start_path": "/nav/0301.html"
        }

        host = source['host']
        start_path = source['start_path']

        language_code = 'de'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        source_url = host + start_path

        pagination = Pagination()
        pagination.add_item(source_url)

        while pagination.has_next():
            page_url = pagination.get_next()

            results_response = requests.request('GET', page_url)
            results_content = results_response.content
            results_soup = BeautifulSoup(results_content, 'html.parser')

            page_content = results_soup.find('div', class_='page-content')
            if page_content is None:
                return True

            ul = page_content.find('ul')
            if ul is None:
                return True

            for li in ul.find_all('li'):
                li_text = li.get_text()
                split_li_text = li_text.split(':')

                date_str = split_li_text[0]
                tmp = datetime.datetime.strptime(date_str, '%d.%m.%Y')
                date = datetime.date(tmp.year, tmp.month, tmp.day)

                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    return True # try another result_link # should be continue

                document_title = split_li_text[1].strip()
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                print("\tdocument_hash:\t", document_folder_md5)

                document_url = ""

                for a in li.find_all('a'):
                    href = a.get('href')
                    if href.endswith('.pdf') is False:
                        continue
                    document_url = href.replace('..', host)
                    break

                if len(document_url) == 0:
                    return True

                document_response = requests.request('GET', document_url)
                document_content = document_response.content

                dirpath = root_path + '/' + document_folder_md5
                try:
                    os.makedirs(dirpath)

                    with open(dirpath + '/' + language_code + '.pdf', 'wb') as f:
                        f.write(document_content)

                    document_text = textract.process(dirpath + '/' + language_code + '.pdf')
                    with open(dirpath + '/' + language_code + '.txt', 'wb') as f:
                        f.write(document_text)

                except FileExistsError:
                    print('Directory path already exists, continue.')

        return True
