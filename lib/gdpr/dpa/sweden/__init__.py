import os
import math
import requests
import json
import datetime
import hashlib
import dateparser
import re
import csv

from .. import DPA

from bs4 import BeautifulSoup

from ...services.links_from_soup_service import links_from_soup_service
from ...services.filename_from_path_service import filename_from_path_service
from ...services.pdf_to_text_service import pdf_to_text_service

from ...specifications import pdf_file_extension_specification
from ...specifications import page_fully_rendered_specification
from ...specifications import gdpr_retention_specification

from ...modules.pagination import Pagination
from ...policies import bulk_collect_location_policy
from ...policies import gdpr_policy

import textract

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ...policies import webdriver_executable_path_policy

class Sweden(DPA):
    def __init__(self):
        iso_code='se'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        language_code = 'se'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        source_url = host + start_path

        source_response = requests.request('GET', source_url)
        source_content = source_response.content
        source_soup = BeautifulSoup(source_content, 'html.parser')

        pagination_list = source_soup.find('ul', class_='pagination-list')
        if pagination_list is None:
            return True

        pagination = Pagination()
        pagination.add_item(source_url)
        for li in pagination_list.find_all('li', class_='list-item'):
            a = li.find('a')
            if a is None:
                return True
            href = a.get('href') # ?p=%d
            pagination.add_item(source_url+href)

        while pagination.has_next():
            page_url = pagination.get_next()
            print('page_url:\t', page_url)

            results_response = requests.request('GET', page_url)
            results_content = results_response.content
            results_soup = BeautifulSoup(results_content, 'html.parser')

            result_list = results_soup.find('ul', class_='result-list')
            if result_list is None:
                return True

            for li in result_list.find_all('li', class_='list-item'):
                item_created = li.find('time', class_='item-created')
                if item_created is None:
                    return True
                date_str = item_created.get_text()
                tmp = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                date = datetime.date(tmp.year, tmp.month, tmp.day)

                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    return True # try another result_link # should be continue

                item_header = li.find('a', class_='item-header')
                if item_header is None:
                    return True

                document_title = item_header.get_text()
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                print("\tdocument_hash:\t", document_folder_md5)

                document_href = item_header.get('href')
                document_url = host + document_href

                document_response = requests.request('GET', document_url)
                document_content = document_response.content
                document_soup = BeautifulSoup(document_content, 'html.parser')

                # area_text -> find pdf link
                area_text = document_soup.find('div', class_='area-text')
                if area_text is None:
                    return True

                pdf_url = ""
                found_pdf = False
                for cand_a in area_text.find_all('a'):
                    cand_href = cand_a.get('href')
                    if cand_href.endswith('.pdf') is False:
                        continue

                    if cand_href.startswith('//'):
                        continue

                    pdf_url = host + cand_href
                    found_pdf = True
                    break

                dirpath = root_path + '/' + document_folder_md5
                try:
                    os.makedirs(dirpath)

                    if found_pdf is True:
                        try:
                            pdf_response = requests.request('GET', pdf_url)
                            pdf_content = pdf_response.content

                            pdf_path = dirpath + '/' + language_code + '.pdf'

                            with open(pdf_path, 'wb') as f:
                                f.write(pdf_content)

                            document_text = textract.process(pdf_path)
                            with open(dirpath + '/' + language_code + '.txt', 'wb') as f:
                                f.write(document_text)
                        except:
                            print('something went wrong trying to get pdf document.')

                    else:
                        document_text = area_text.get_text()
                        with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                            f.write(document_text)

                except FileExistsError:
                    print('Directory path already exists, continue.')

            pagination_list = results_soup.find('ul', class_='pagination-list')
            if pagination_list is None:
                return True
            for li in pagination_list.find_all('li', class_='list-item'):
                a = li.find('a')
                if a is None:
                    return True
                href = a.get('href') # ?p=%d
                pagination.add_item(source_url+href)

        return True
