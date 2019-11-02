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

class Poland(DPA):
    def __init__(self):
        iso_code='po'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        language_code = 'pl'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        results_url = host + start_path

        pagination = Pagination()
        pagination.add_link(results_url)

        while pagination.has_next():
            page_url = pagination.get_next()
            print('page_url:\t', page_url)

            results_response = requests.request('GET', results_url)
            results_html = results_response.content
            results_soup = BeautifulSoup(results_html, 'html.parser')

            decisions_container = results_soup.find('div', id='decisions-container')
            if decisions_container is None:
                return None

            for decision in decisions_container.find_all('div', class_='decision'):
                date_div = decision.find('div', class_='float-sm-right')
                if date_div is None:
                    return None
                date_str = date_div.get_text()
                tmp = dateparser.parse(date_str, languages=[language_code])
                date = datetime.date(tmp.year, tmp.month, tmp.day)

                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    continue # try another result_link

                a = decision.find('a')
                if a is None:
                    return None

                document_title = a.get_text()
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

                document_href = a.get('href')
                document_url = document_href
                print("\tdocument_hash:\t", document_folder_md5)
                try:
                    document_response = requests.request('GET', document_url)
                    document_content = document_response.content
                except:
                    print('Something went wrong trying to get the document')

                dirpath = root_path + '/' + document_folder_md5
                try:
                    os.makedirs(dirpath)
                except FileExistsError:
                    print('Directory path already exists, continue.')

                document_soup = BeautifulSoup(document_content, 'html.parser')
                article_content = document_soup.find('div', id='article-content')
                if article_content is None:
                    return None

                document_text = article_content.get_text()
                with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                    f.write(document_text)

        return True
