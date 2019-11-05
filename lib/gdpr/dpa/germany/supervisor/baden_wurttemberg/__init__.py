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

class BadenWurttemberg(DPA):
    def __init__(self):
        iso_code='de'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = {
            "host": "https://www.baden-wuerttemberg.datenschutz.de",
            "start_path": "/pressemitteilungen"
        }

        host = source['host']
        start_path = source['start_path']

        language_code = 'de'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        results_url = host + start_path

        exec_path = webdriver_executable_path_policy.path_for_system()

        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        driver = webdriver.Chrome(options=options, executable_path=exec_path)
        driver.get(results_url)
        try:
            print('page_source', results_url)
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            results_content = driver.page_source
            results_soup = BeautifulSoup(results_content, 'html.parser')

            post_content = results_soup.find('div', class_='post-content')
            if post_content is None:
                return True

            paragraphs = post_content.find_all('p', recursive=False)
            paragraphs = list(filter(lambda p: len(p.get_text().strip()) > 0, paragraphs))

            tables = post_content.find_all('table', recursive=False)

            if len(paragraphs) != len(tables):
                return True

            for i in range(len(tables)):
                p = paragraphs[i]
                table = tables[i]

                year_str = p.get_text().strip()

                for tr in table.find_all('tr'):
                    tds = tr.find_all('td')

                    date_index = 0
                    doc_index = 1

                    if len(tds) != max(date_index, doc_index) + 1:
                        return True

                    part_date_str = tds[date_index].get_text()
                    if part_date_str.endswith('.') is False:
                        part_date_str += '.'
                    date_str = part_date_str + year_str
                    tmp = datetime.datetime.strptime(date_str, '%d.%m.%Y')
                    date = datetime.date(tmp.year, tmp.month, tmp.day)

                    if gdpr_retention_specification.is_satisfied_by(date) is False:
                        return True # try another result_link # should be continue

                    document_td = tds[doc_index]
                    document_a = document_td.find('a')
                    if document_a is None:
                        return True

                    document_title = document_a.get_text()
                    document_folder = document_title
                    document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

                    document_href = document_a.get('href')
                    document_url = document_href
                    if document_href.endswith('.pdf') is False:
                        continue

                    print("\tdocument_hash:\t", document_folder_md5)

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
        finally:
            driver.quit()


        return True
