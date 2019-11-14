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

class Hungary(DPA):
    def __init__(self):
        country_code='HU'
        super().__init__(country_code)

    def get_docs(self):
        if bulk_collect_location_policy.is_allowed(self.path) is False:
            raise ValueError('Bulk collect path is illegal ' + self.path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']
        render_type = source['render_type']

        folder_name = self.country.replace(' ', '-').lower()
        root_path = self.path + '/' + folder_name

        page_url = host + start_path

        results_response = requests.request('GET', page_url)
        results_html = results_response.content
        results_soup = BeautifulSoup(results_html, 'html.parser')

        result_target_element = target_element['results']
        element = result_target_element.split('.')[0]
        class_ = result_target_element.split('.')[1]

        table = results_soup.find(element, class_=class_)
        rows = table.find_all('tr')
        for i in range(1, len(rows)): # skip the first and last row
            row = rows[i]
            date_cell = row.find(target_element['date'].split('.')[0], class_=target_element['date'].split('.')[1])
            date_str = date_cell.get_text().strip()

            if len(date_str) == 0 or date_str is None:
                continue

            # eg: 2019.01.28
            tmp = datetime.datetime.strptime(date_str, '%Y.%m.%d')
            date = datetime.date(tmp.year, tmp.month, tmp.day)

            if gdpr_retention_specification.is_satisfied_by(date) is False:
                continue # try another result_link

            title = row.find('td', 'imW402')
            document_folder = title.get_text().strip()
            document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
            print('Collecting doc with hash:\t', document_folder_md5)

            language_code = 'hu'

            document_link = links_from_soup_service(row.find('td', 'imW90'))[0]
            document_url = host + '/' + document_link[1]
            document_response = requests.request('GET', document_url)
            document_content = document_response.content

            dirpath = root_path + '/' + document_folder_md5
            try:
                os.makedirs(dirpath)
            except FileExistsError:
                print('Directory path already exists, continue.')

            document_pdf_path = dirpath + '/' + language_code + '.pdf'

            with open(document_pdf_path, 'wb') as f:
                f.write(document_content)

            document_text = textract.process(document_pdf_path)
            with open(dirpath + '/' + language_code + '.txt', 'wb') as f:
                f.write(document_text)

        return True
