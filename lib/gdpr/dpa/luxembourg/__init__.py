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

class Luxembourg(DPA):
    def __init__(self):
        iso_code='lu'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        now = datetime.datetime.now()
        gdpr_date = gdpr_policy.implementation_date()

        year_range = range(gdpr_date.year, now.year + 1)

        pagination = Pagination()
        for year in year_range:
            page_url = host + start_path + '?r=f%2Faem_first_released%2F{year}&'.format(year=year)
            pagination.add_link(page_url)

        while pagination.has_next():
            result_url = pagination.get_next()
            print('page_url:', result_url)

            result_response = requests.request('GET', result_url)
            results_html = result_response.content
            results_soup = BeautifulSoup(results_html, 'html.parser')

            ol = results_soup.find('ol', class_='search-results')
            for li in ol.find_all('li'):
                article_metas = li.find('ul', class_='article-metas')
                if article_metas is None:
                    continue

                time = article_metas.find('time', class_='article-published')
                # 21/12/2018
                date_str = time.get_text()
                tmp = datetime.datetime.strptime(date_str, '%d/%m/%Y')
                date = datetime.date(tmp.year, tmp.month, tmp.day)
                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    continue # try another result_link

                document_title, document_href = links_from_soup_service(li)[0]
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                document_url = host + document_href

                language_code = 'fr'

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

                aside = document_soup.find('aside', class_='page-more')
                pdf_title, pdf_href = links_from_soup_service(aside)[0]

                if pdf_href.endswith('.pdf') is False:
                    continue

                pdf_url = 'https:' + pdf_href
                print('\tpdf_url:', pdf_url)
                try:
                    pdf_response = requests.request('GET', pdf_url)
                    pdf_content = pdf_response.content
                except:
                    print('something went wrong trying to get document')

                document_pdf_path = dirpath + '/' + language_code + '.pdf'

                with open(document_pdf_path, 'wb') as f:
                    f.write(pdf_content)

                document_text = textract.process(document_pdf_path)

                with open(dirpath + '/' + language_code + '.txt', 'wb') as f:
                    f.write(document_text)

        return True
