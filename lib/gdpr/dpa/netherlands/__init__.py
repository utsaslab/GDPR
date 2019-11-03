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

class Netherlands(DPA):
    def __init__(self):
        iso_code='nl'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        language_code = 'nl'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        results_url = host + start_path

        results_response = requests.request('GET', results_url)
        results_html = results_response.content
        results_soup = BeautifulSoup(results_html, 'html.parser')

        pagination = Pagination()
        pagination.add_item(host + start_path)

        pager = results_soup.find('div', class_='pager')
        ul_pager = pager.find('ul')
        for li in ul_pager.find_all('li'):
            a = li.find('a')
            if a is None:
                continue
            link = a.get('href')
            pagination.add_item(host + link)

        while pagination.has_next():
            page_url = pagination.get_next()
            print('page_url:\t', page_url)

            results_response = requests.request('GET', page_url)
            results_html = results_response.content
            results_soup = BeautifulSoup(results_html, 'html.parser')

            article_list = results_soup.find('ul', class_='article-list')
            for li in article_list.find_all('li'):
                date_span = li.find('span', class_='date')
                if date_span is None:
                    return True

                date_str = date_span.get_text()
                tmp = dateparser.parse(date_str, languages=[language_code])
                date = datetime.date(tmp.year, tmp.month, tmp.day)

                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    continue # try another result_link

                linktitle = li.find('span', class_='linktitle')
                if linktitle is None:
                    return True

                document_title = linktitle.get_text()
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                print("\tdocument_hash:\t", document_folder_md5)

                divcontent = li.find('div', class_='content')
                if divcontent is None:
                    return True

                divcontent_a = divcontent.find('a')
                if divcontent_a is None:
                    return True

                document_href = divcontent_a.get('href')
                document_url = document_href
                try:
                    document_response = requests.request('GET', document_url)
                    document_content = document_response.content
                except:
                    print('Something went wrong trying to get the document')

                if document_url.endswith('.pdf') is False:
                    return True

                dirpath = root_path + '/' + document_folder_md5
                try:
                    os.makedirs(dirpath)
                except FileExistsError:
                    print('Directory path already exists, continue.')

                with open(dirpath + '/' + language_code + '.pdf', 'wb') as f:
                    f.write(document_content)

                document_text = textract.process(dirpath + '/' + language_code + '.pdf')
                with open(dirpath + '/' + language_code + '.txt', 'wb') as f:
                    f.write(document_text)

            pager = results_soup.find('div', class_='pager')
            ul_pager = pager.find('ul')
            for li in ul_pager.find_all('li'):
                a = li.find('a')
                if a is None:
                    continue
                link = a.get('href')
                pagination.add_item(host + link)

        return True
