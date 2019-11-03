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

class Slovakia(DPA):
    def __init__(self):
        iso_code='sk'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        language_code = 'sk'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        source_url = host+start_path
        source_response = requests.request('GET', source_url)
        source_content = source_response.content
        source_soup = BeautifulSoup(source_content, 'html.parser')

        pager = source_soup.find('ul', class_='pager')
        if pager is None:
            return True

        pagination = Pagination()
        for li in pager.find_all('li', class_='pager-item'):
            a = li.find('a')
            if a is None:
                continue
            href = a.get('href')
            pagination.add_item(host + href)

        while pagination.has_next():
            page_url = pagination.get_next()
            print('page_url:\t', page_url)

            results_response = requests.request('GET', page_url)
            results_content = results_response.content
            results_soup = BeautifulSoup(results_content, 'html.parser')

            view_content_index = 1
            view_contents = results_soup.find_all('div', class_='view-content')
            if len(view_contents) < view_content_index + 1:
                return True
            view_content = view_contents[view_content_index]

            for views_row in view_content.find_all('div', class_='views-row'):
                b = views_row.find('b')
                if b is None:
                    return True

                date_str = b.get_text().split(' - ')[0]
                # eg. 30.10.2019
                tmp = datetime.datetime.strptime(date_str, '%d.%m.%Y')
                date = datetime.date(tmp.year, tmp.month, tmp.day)

                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    continue # try another result_link # should be continue

                h2 = views_row.find('h2')
                if h2 is None:
                    return True

                h2_a = h2.find('a')
                if h2_a is None:
                    return True

                document_title = h2_a.get_text()
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                print("\tdocument_hash:\t", document_folder_md5)

                document_href = h2_a.get('href')
                document_url = host + document_href
                try:
                    document_response = requests.request('GET', document_url)
                    document_content = document_response.content
                    document_soup = BeautifulSoup(document_content, 'html.parser')
                    field_items = document_soup.find_all('div', class_='field-items')
                    if len(field_items) == 0:
                        return True

                    field_item = field_items[0]
                    document_text = field_item.get_text()

                    dirpath = root_path + '/' + document_folder_md5
                    try:
                        os.makedirs(dirpath)

                        with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                            f.write(document_text)

                        print_pdf = document_soup.find('span', class_='print_pdf')

                        if print_pdf is None:
                            continue

                        print_pdf_a = print_pdf.find('a')

                        if print_pdf_a is None:
                            continue

                        print_pdf_href = print_pdf_a.get('href')

                        pdf_response = requests.request('GET', print_pdf_href)
                        pdf_content = pdf_response.content

                        with open(dirpath + '/' + language_code + '.pdf', 'wb') as f:
                            f.write(pdf_content)

                    except FileExistsError:
                        print('Directory path already exists, continue.')
                except:
                    print('Something went wrong trying to get the document')

            pager = results_soup.find('ul', class_='pager')
            if pager is None:
                return True

            for li in pager.find_all('li', class_='pager-item'):
                a = li.find('a')
                if a is None:
                    continue
                href = a.get('href')
                pagination.add_item(host + href)

        return True
