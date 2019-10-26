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

class Latvia(DPA):
    def __init__(self):
        iso_code='LV'
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

        pagination = Pagination()
        pagination.add_link(page_url)

        pagination_links = links_from_soup_service(results_soup, target_element['pagination'])
        for number, pagination_url in pagination_links:
            pagination.add_link(pagination_url)

        while pagination.has_next() is True:
            pagination_url = pagination.get_next()
            print('pagination_url:', pagination_url)

            result_response = requests.request('GET', pagination_url)
            results_html = result_response.content
            results_soup = BeautifulSoup(results_html, 'html.parser')

            split_result_target_element = target_element['results'].split('#')
            split_date_target_element = target_element['date'].split('.')

            results_target_area = results_soup.find(split_result_target_element[0], id=split_result_target_element[1])
            posts = results_target_area.find_all('div', class_='post')
            for post in posts:
                meta = post.find(split_date_target_element[0], class_=split_date_target_element[1])
                # eg. 15.10.2019
                date_str = meta.find('strong').get_text().rstrip('.')
                tmp = datetime.datetime.strptime(date_str, '%d.%m.%Y')
                date = datetime.date(tmp.year, tmp.month, tmp.day)

                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    continue # try another result_link

                h2 = post.find('h2')

                document_title, document_url = links_from_soup_service(h2)[0]
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

                print('\tdocument_folder_md5:', document_folder_md5)

                language_code = 'lv'

                try:
                    document_response = requests.request('GET', document_url)
                    document_content = document_response.content
                    document_html = BeautifulSoup(document_content, 'html.parser')
                except:
                    print('something went wrong trying to get document')

                dirpath = root_path + '/' + document_folder_md5
                try:
                    os.makedirs(dirpath)
                except FileExistsError:
                    print('Directory path already exists, continue.')

                split_document_target_element = target_element['document'].split('.')
                document_target_area = document_html.find(split_document_target_element[0], class_=split_document_target_element[1])

                if document_target_area is not None:
                    document_text = document_target_area.get_text()

                    with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                        f.write(document_text)

            pagination_links = links_from_soup_service(results_soup, target_element['pagination'])
            for number, pagination_url in pagination_links:
                pagination.add_link(pagination_url)

        return True
