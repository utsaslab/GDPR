import os
import shutil
import math
import requests
import json

from .. import DPA

from bs4 import BeautifulSoup

from ...services.links_from_soup_service import links_from_soup_service
from ...services.filename_from_path_service import filename_from_path_service
from ...services.pdf_to_text_service import pdf_to_text_service

from ...specifications import pdf_file_extension_specification
from ...specifications import page_fully_rendered_specification

from ...modules.pagination import Pagination
from ...policies import bulk_collect_location_policy

class Crotia(DPA):
    def __init__(self):
        iso_code='HR'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal: ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']
        render_type = source['render_type']

        pagination = Pagination()
        pagination.add_link(host + start_path)

        try:
            result_response = requests.request('GET', host + start_path)
            result_html = result_response.content # .content = bytes, .text = str (already encoded)
            result_soup = BeautifulSoup(result_html, 'html.parser')
        except:
            print('Something went wrong. Could not get response.')

        root_path = path + self.iso_code
        result_links = links_from_soup_service(result_soup, target_element=target_element['results'])
        for link in result_links:
            result_title = link[0]
            result_url = link[1]

            try:
                document_response = requests.request('GET', result_url)
                document_html = document_response.text
                document_soup = BeautifulSoup(document_html, 'html.parser')
            except:
                print('Something went wrong. Could not get response.')

            target_area = document_soup.find('div', class_=target_element['document'].split('.')[1])
            document_text = target_area.get_text()

            filename = result_title.lower().replace(' ', '-')
            dirpath = root_path + '/' + filename
            try:
                os.makedirs(dirpath)
            except FileExistsError:
                print('file already exists, continue.')

            with open(dirpath + '/hr.txt', 'w') as f:
                f.write(document_text)

        return True
