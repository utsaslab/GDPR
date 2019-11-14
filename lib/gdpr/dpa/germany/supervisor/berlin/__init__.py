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

class Berlin(DPA):
    def __init__(self):
        country_code='de'
        super().__init__(country_code)

    def get_docs(self):
        if bulk_collect_location_policy.is_allowed(self.path) is False:
            raise ValueError('Bulk collect path is illegal ' + self.path)

        source = {
            "host": "https://www.datenschutz-berlin.de",
            "start_path": "/infothek-und-service/pressemitteilungen/"
        }

        host = source['host']
        start_path = source['start_path']

        language_code = 'de'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = self.path + '/' + folder_name

        source_url = host + start_path

        pagination = Pagination()
        pagination.add_item(source_url)

        while pagination.has_next():
            page_url = pagination.get_next()
            print('page_url:', page_url)

            results_response = requests.request('GET', page_url)
            results_content = results_response.content
            results_soup = BeautifulSoup(results_content, 'html.parser')

            sections = results_soup.find_all('section', class_='causes-single-wrapper')
            for i in range(1, len(sections)):
                section = sections[i]

                press_date = section.find('div', class_='press-date')
                if press_date is None:
                    return True

                date_str = press_date.get_text().strip('')
                tmp = dateparser.parse(date_str, languages=[language_code])
                date = datetime.date(tmp.year, tmp.month, tmp.day)

                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    return True # try another result_link # should be continue

                h4 = section.find('h4')
                if h4 is None:
                    return True

                document_title = h4.get_text()
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                print("\tdocument_hash:\t", document_folder_md5)

                sidebar = section.find('div', class_='sidebar')
                if sidebar is None:
                    return True

                document_links = sidebar.find_all('a')
                if len(document_links) == 0:
                    return True

                dirpath = root_path + '/' + document_folder_md5
                try:
                    os.makedirs(dirpath)

                    for a in document_links:
                        document_href = a.get('href')
                        a_text = a.get_text().strip()

                        # overwrite language code
                        # depending on document language title suffix labels: (englisch) | (deutsch).
                        if a_text.endswith('(englisch)') is True:
                            language_code = 'en'
                        else:
                            language_code = 'de'

                        document_url = host + document_href

                        try:
                            document_response = requests.request('GET', document_url)
                            document_content = document_response.content

                            with open(dirpath + '/' + language_code + '.pdf', 'wb') as f:
                                f.write(document_content)

                            document_text = textract.process(dirpath + '/' + language_code + '.pdf')
                            with open(dirpath + '/' + language_code + '.txt', 'wb') as f:
                                f.write(document_text)
                        except:
                            print('Something went wrong getting document.')

                except FileExistsError:
                    print('Directory path already exists, continue.')

        return True
