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

class Romania(DPA):
    def __init__(self):
        iso_code='ro'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        language_code = 'ro'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        pagination = Pagination()
        pagination.add_link(host + start_path)

        while pagination.has_next():
            page_url = pagination.get_next()

            print('page_url:', page_url)

            results_response = requests.request('GET', page_url)
            results_html = results_response.content
            results_soup = BeautifulSoup(results_html, 'html.parser')

            rectangle_scroll = results_soup.find('div', id='rectangle_scroll')
            if rectangle_scroll is None:
                return True

            date_index = 0
            doc_title_index = 2
            doc_href_index = 3

            paragraphs = rectangle_scroll.find_all('p')

            #if len(paragraphs) < max([date_index, doc_title_index, doc_href_index]) + 1:
            #    return True

            for i in range(1, len(paragraphs)): # used to be 5
                p_date = paragraphs[i]

                date_str = p_date.get_text()
                tmp = None
                try:
                    tmp = datetime.datetime.strptime(date_str, '%d/%m/%Y')
                except ValueError:
                    print('')

                if tmp is None:
                    continue

                date = datetime.date(tmp.year, tmp.month, tmp.day)

                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    return True # try another result_link # should be continue

                p_title = paragraphs[i+1]
                p_href = None

                j = 0
                j_threshold = 4
                while p_href is None:
                    p_cand = paragraphs[i+j]
                    p_href = p_cand.find('a')
                    if j == j_threshold:
                        break
                    j += 1

                if p_href is None:
                    return True

                document_title = p_title.get_text()
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                print("\tdocument_hash:\t", document_folder_md5)

                document_href = p_href.get('href')

                document_url = host + document_href
                try:
                    document_response = requests.request('GET', document_url)
                    document_content = document_response.content
                    document_soup = BeautifulSoup(document_content, 'html.parser')

                    document_target_area = document_soup.find('div', id='rectangle_scroll')
                    if document_target_area is None:
                        continue
                    document_text = document_target_area.get_text()

                    dirpath = root_path + '/' + document_folder_md5
                    try:
                        os.makedirs(dirpath)

                        with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                            f.write(document_text)

                    except FileExistsError:
                        print('Directory path already exists, continue.')

                except:
                    print('Something went wrong trying to get the document')

        return True
