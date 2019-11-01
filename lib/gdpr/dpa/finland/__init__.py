import os
import math
import requests
import json
import datetime
import hashlib

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

class Finland(DPA):
    def __init__(self):
        iso_code='FI'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal: ' + path)

        for source in self.sources:
            host = source['host']
            start_path = source['start_path']
            target_element = source['target_element']
            render_type = source['render_type']

            pagination = Pagination()
            pagination.add_link(host + start_path)

            folder_name = self.country.replace(' ', '-').lower()
            root_path = path + '/' + folder_name

            while pagination.has_next():
                page_url = pagination.get_next()
                try:
                    results_response = requests.request('GET', page_url)
                    results_html = results_response.content
                    results_soup = BeautifulSoup(results_html, 'html.parser')
                except:
                    print("Something went wrong.")

                result_links = links_from_soup_service(results_soup, target_element=target_element['results'])

                for result_link in result_links:
                    result_title = result_link[0]
                    result_url = result_link[1]

                    try:
                        document_response = requests.request('GET', host + result_url)
                        document_html = document_response.content
                        document_soup = BeautifulSoup(document_html, 'html.parser')
                    except:
                        print("Something went wrong.")

                    document_folder = result_title
                    document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

                    dirpath = root_path + '/' + document_folder_md5
                    try:
                        os.makedirs(dirpath)
                    except FileExistsError:
                        print('file already exists, continue.')

                    language_code = 'fi'
                    
                    document_area = document_soup.find('div', class_=target_element['document'].split('.')[-1])
                    document_text = document_area.get_text()

                    with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                        f.write(document_text)

        return True
