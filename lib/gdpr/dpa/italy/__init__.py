import os
import math
import requests
import json
import datetime
import hashlib
import dateparser
import re

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

class Italy(DPA):
    def __init__(self):
        iso_code='IT'
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

        page_url = host + start_path

        result_response = requests.request('GET', page_url)
        results_html = result_response.content
        results_soup = BeautifulSoup(results_html, 'html.parser')

        split_result_target_element = target_element['results'].split('.')

        target_areas = results_soup.find_all(split_result_target_element[0], class_=split_result_target_element[1])

        result_target_area = target_areas[2]

        ul = result_target_area.find('ul')
        for li in ul.find_all('li', recursive=False):
            em = li.find('em')
            if em is None: # cannot determine date of document
                continue
            em_text = em.get_text()

            date_str = em_text.lstrip('(').rstrip(')').split(",")[-1].strip()
            tmp = dateparser.parse(date_str, languages=['it'])
            date = datetime.date(tmp.year, tmp.month, tmp.day)
            print('date:', date.year, date.month, date.day)

            if gdpr_retention_specification.is_satisfied_by(date) is False:
                continue # try another result_link

            document_title, document_href = links_from_soup_service(li)[0]
            document_folder = document_title
            document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
            document_url = host + document_href

            language_code = 'it'

            try:
                document_response = requests.request('GET', document_url)
                document_content = document_response.content
                document_html = BeautifulSoup(document_content, 'html.parser')
                print('docurl:', document_url)
            except:
                print('something went wrong trying to get document')

            dirpath = root_path + '/' + document_folder_md5
            try:
                os.makedirs(dirpath)
            except FileExistsError:
                print('Directory path already exists, continue.')

            split_document_target_element = target_element['document'].split('#')
            document_target_area = document_html.find(split_document_target_element[0], id=split_document_target_element[1])

            if document_target_area is not None:
                document_text = document_target_area.get_text()

                with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                    f.write(document_text)

            else: # check for multimedia or other
                document_target_area = document_html.find('div', class_="testo")
                document_links = links_from_soup_service(document_target_area)
                if len(document_links) == 0:
                    continue

                # assuming one multimedia link per document.
                document_link = document_links[0]
                document_url = host + document_link[1]

                document_header = requests.head(document_url)
                content_type = document_header.headers['Content-Type']
                format_ = content_type.split('/')[-1]

                audio_response = requests.request('GET', document_url)
                audio_content = audio_response.content

                with open(dirpath + '/' + language_code + '.' + format_, 'wb') as f:
                    f.write(audio_content)

        return True
