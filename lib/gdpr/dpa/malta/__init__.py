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

class Malta(DPA):
    def __init__(self):
        iso_code='mt'
        super().__init__(iso_code)

    def bulk_collect(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        results_url = host + start_path

        result_response = requests.request('GET', results_url)
        results_html = result_response.content
        results_soup = BeautifulSoup(results_html, 'html.parser')

        columnB = results_soup.find('div', class_='b')
        if columnB is None:
            return True

        content = columnB.find('div', class_='content')
        if content is None:
            return True

        table = content.find('table', id='ctl00_SPWebPartManager1_g_66c3adf3_e48a_477c_8c0d_d4ce601f252a_ctl00_grdListItems')
        if table is None:
            return True

        for tr in table.find_all('tr'):
            spans = tr.find_all('span')
            if len(spans) != 3:
                continue

            date_index = 0
            reference_index = 1
            link_index = 2

            date_str = spans[date_index].get_text()
            tmp = datetime.datetime.strptime(date_str, '%d/%m/%Y')
            date = datetime.date(tmp.year, tmp.month, tmp.day)

            if gdpr_retention_specification.is_satisfied_by(date) is False:
                continue # try another result_link

            link = spans[link_index]

            document_title, document_href = links_from_soup_service(link)[0]
            document_folder = document_title
            document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
            document_url = host + document_href

            print('doc:\t', document_folder_md5)

            language_code = 'en'

            try:
                document_response = requests.request('GET', document_url)
                document_content = document_response.content
                document_soup = BeautifulSoup(document_content, 'html.parser')
            except:
                print('something went wrong trying to get document')

            dirpath = root_path + '/' + document_folder_md5
            try:
                os.makedirs(dirpath)
            except FileExistsError:
                print('Directory path already exists, continue.')

            doc_column_b = document_soup.find('div', class_='b')
            if doc_column_b is None:
                continue

            doc_content = doc_column_b.find('div', class_='content')
            if doc_content is None:
                continue

            divs = doc_content.find_all('div', recursive=False)
            if len(divs) != 4:
                continue

            doc_body_index = 2
            doc_body = divs[doc_body_index]
            if doc_body is None:
                continue

            document_text = doc_body.get_text()
            # source: https://stackoverflow.com/questions/3711856/how-to-remove-empty-lines-with-or-without-whitespace-in-python/32338035
            document_text = '\n'.join([line for line in document_text.split('\n') if line.strip() != ''])
            document_text = document_text.lstrip('Page Content')

            with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                f.write(document_text)

        return True
