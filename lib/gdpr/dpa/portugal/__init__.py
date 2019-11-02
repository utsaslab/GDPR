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

class Portugal(DPA):
    def __init__(self):
        iso_code='pt'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        language_code = 'pt'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        pagination = Pagination()

        now = datetime.datetime.now()
        gdpr_date = gdpr_policy.implementation_date()
        year_range = range(gdpr_date.year, now.year+1)
        for year in year_range:
            results_url = host + f"/bin/decisoes/decisoes.asp?primeira_escolha={year}&segunda_escolha=40"
            pagination.add_link(results_url)

        while pagination.has_next():
            page_url = pagination.get_next()
            print('page_url:', page_url)

            results_response = requests.request('GET', page_url)
            results_html = results_response.content
            results_soup = BeautifulSoup(results_html, 'html.parser')

            table_index = 3
            tables = results_soup.find_all('table')
            if len(tables) < table_index+1:
                return None

            table = tables[table_index]
            if table is None:
                return None

            for tr in table.find_all('tr', recursive=False):
                a = tr.find('a')
                if a is None:
                    continue

                # not a real date per say.
                # eg. 48/ 2019

                document_title = a.get_text()
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

                document_href = a.get('href')
                document_url = document_href
                print("\tdocument_hash:\t", document_folder_md5)
                try:
                    document_response = requests.request('GET', document_url)
                    document_content = document_response.content

                    if document_url.endswith('.pdf') is False:
                        return True

                    dirpath = root_path + '/' + document_folder_md5
                    try:
                        os.makedirs(dirpath)

                        with open(dirpath + '/' + language_code + '.pdf', 'wb') as f:
                            f.write(document_content)

                        document_text = pdf_to_text_service(dirpath + '/' + language_code + '.pdf')
                        with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                            f.write(document_text)

                    except FileExistsError:
                        print('Directory path already exists, continue.')

                except:
                    print('Something went wrong trying to get the document')

        return True
