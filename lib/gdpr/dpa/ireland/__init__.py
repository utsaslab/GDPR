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

class Ireland(DPA):
    def __init__(self):
        iso_code='IE'
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
        split_date_target_element = target_element['date'].split('.')

        result_target_area = results_soup.find(split_result_target_element[0], class_=split_result_target_element[1])
        ul = result_target_area.find('ul')
        for li in ul.find_all('li', recursive=False):
            date_str = li.find(split_date_target_element[0], class_=split_date_target_element[1]).get_text()

            regex = r"(\d\d)(st|nd|rd|th) (\w*) (\d\d\d\d)"

            matches = re.finditer(regex, date_str)
            matches = list(matches)
            if len(matches) == 0:
                continue

            match = matches[0]
            groups = match.groups()
            date_suffix_group_num = 2

            date_str = date_str[:match.start(date_suffix_group_num)] + date_str[match.end(date_suffix_group_num):]

            # ex. 16th August 2019
            tmp = datetime.datetime.strptime(date_str, '%d %B %Y')
            date = datetime.date(tmp.year, tmp.month, tmp.day)

            if gdpr_retention_specification.is_satisfied_by(date) is False:
                continue # try another result_link

            document_title, document_path = links_from_soup_service(li)[0]

            document_folder = document_title
            document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

            document_url = host + document_path

            language_code = 'en'

            document_response = requests.request('GET', document_url)
            document_content = document_response.content
            document_html = BeautifulSoup(document_content, 'html.parser')

            dirpath = root_path + '/' + document_folder_md5
            try:
                os.makedirs(dirpath)
            except FileExistsError:
                print('Directory path already exists, continue.')

            split_document_target_element = target_element['document'].split('.')
            document_target_area = document_html.find(split_document_target_element[0], class_=split_document_target_element[1])
            document_text = document_target_area.get_text()

            with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                f.write(document_text)

        return True
