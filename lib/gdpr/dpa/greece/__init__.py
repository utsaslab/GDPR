import os
import math
import requests
import json
import datetime
import hashlib
import dateparser

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

class Greece(DPA):
    def __init__(self):
        iso_code='GR'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']
        render_type = source['render_type']

        # find the 2nd nested tbody.

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        page_url = host + start_path
        results_response = requests.request('GET', page_url)
        results_html = results_response.content
        results_soup = BeautifulSoup(results_html, 'html.parser')

        tables = results_soup.find_all('table')
        results_table_index = 7
        results_table = tables[results_table_index]

        paragraphs = results_table.find_all('p')
        for i in range(0, len(paragraphs)-1, 2):
            p = paragraphs[i]
            p_next = paragraphs[i+1]

            if ("Press Release" in p.get_text()) == False:
                continue

            date_str = p.get_text().split(' - ')[0].strip()
            tmp = dateparser.parse(date_str)
            date = datetime.date(tmp.year, tmp.month, tmp.day)

            if gdpr_retention_specification.is_satisfied_by(date) is False:
                continue # try another result_link

            document_folder = p.get_text()
            document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

            language_code = 'en'

            document_link = links_from_soup_service(p_next)[0]
            document_url = document_link[1]
            document_response = requests.request('GET', document_url)
            document_content = document_response.content

            dirpath = root_path + '/' + document_folder_md5
            try:
                os.makedirs(dirpath)
            except FileExistsError:
                print('Directory path already exists, continue.')

            document_word_path = dirpath + '/' + language_code + '.doc'

            with open(document_word_path, 'wb') as f:
                f.write(document_content)

            document_text = textract.process(document_word_path)
            with open(dirpath + '/' + language_code + '.txt', 'wb') as f:
                f.write(document_text)

        return True
