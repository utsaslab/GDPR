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

class Austria(DPA):
    def __init__(self):
        iso_code='AT'
        super().__init__(iso_code)

    def bulk_collect(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal: ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']
        render_type = source['render_type']

        # uncomment to test pagination.
        # start_path = '/Ergebnis.wxe?Abfrage=Dsk&Entscheidungsart=Undefined&Organ=Undefined&SucheNachRechtssatz=True&SucheNachText=True&GZ=&VonDatum=25.08.1991&BisDatum=23.09.2019&Norm=&ImRisSeitVonDatum=&ImRisSeitBisDatum=&ImRisSeit=Undefined&ResultPageSize=100&Suchworte=&Position=1&SkipToDocumentPage=true'

        pagination = Pagination()
        pagination.add_link(start_path)

        response = requests.request('GET', host + start_path)
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')

        pagination_links = links_from_soup_service(soup, target_element=target_element['pagination'])
        for link in pagination_links:
            title = link[0]
            path = link[1]
            if title.isdigit() is False:
                continue

            pagination.add_link(path)

        while(pagination.has_next()):
            page_ref = pagination.get_next()

            if page_fully_rendered_specification.is_satisfied_by(render_type) is False:
                break

            if page_ref != start_path:
                response = requests.request('GET', host + page_ref)
                html_doc = response.text
                soup = BeautifulSoup(html_doc, 'html.parser')

            root_path = path + self.iso_code
            result_links = links_from_soup_service(soup, target_element=target_element['results'])
            for link in result_links:
                # title = link[0]
                path = link[1]
                if pdf_file_extension_specification.is_satisfied_by(path) is True:
                    filename = filename_from_path_service(path)
                    response = requests.request('GET', host + path)

                    dirpath = root_path + '/' + filename
                    try:
                        os.makedirs(dirpath)
                    except FileExistsError:
                        print('file already exists, continue.')

                    with open(dirpath + '/original.pdf', 'wb') as f:
                        f.write(response.content)

                    text = pdf_to_text_service(dirpath + '/original.pdf')
                    with open(dirpath + '/original.txt', 'w') as f:
                        f.write(text)

            pagination_links = links_from_soup_service(soup, target_element=target_element['pagination'])
            for link in pagination_links:
                title = link[0]
                path = link[1]
                if title.isdigit() is False:
                    continue

                pagination.add_link(path)

        return True
