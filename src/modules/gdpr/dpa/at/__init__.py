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
from ...modules.pagination import Pagination

class AT(DPA):
    def __init__(self):
        country_code='AT'
        super().__init__(country_code)

    def get_penalties(self):
        penalties = []

        with open('./modules/gdpr/assets/supported-dpas.json', 'r') as f:
            supported_dpas = json.load(f)

        dpa = supported_dpas[self.country_code]
        sources = dpa['sources']
        host = next(iter(sources))

        source = sources[host]
        init_path = source['init_path']
        target_element = source['target_element']
        render_type = source['render_type']

        # uncomment to test pagination.
        # init_path = '/Ergebnis.wxe?Abfrage=Dsk&Entscheidungsart=Undefined&Organ=Undefined&SucheNachRechtssatz=True&SucheNachText=True&GZ=&VonDatum=25.08.1991&BisDatum=23.09.2019&Norm=&ImRisSeitVonDatum=&ImRisSeitBisDatum=&ImRisSeit=Undefined&ResultPageSize=100&Suchworte=&Position=1&SkipToDocumentPage=true'

        pagination = Pagination()
        pagination.add_link(init_path)

        response = requests.request('GET', host + init_path)
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

            if render_type != 'FULLY_RENDERED':
                break

            if page_ref != init_path:
                response = requests.request('GET', host + page_ref)
                html_doc = response.text
                soup = BeautifulSoup(html_doc, 'html.parser')

            # handle result_links here.
            result_links = links_from_soup_service(soup, target_element=target_element['results'])
            root_path = './data/' + self.country_code

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

            #shutil.rmtree(root_path, ignore_errors=True)

            pagination_links = links_from_soup_service(soup, target_element=target_element['pagination'])
            for link in pagination_links:
                title = link[0]
                path = link[1]
                if title.isdigit() is False:
                    continue

                pagination.add_link(path)

        #article_links = links_from_soup_service(soup, target_element=target_element['articles'])
        #print(json.dumps(article_links, indent=4))

        #with open('./modules/gdpr/assets/at-links.json', 'w') as outfile:
        #    json.dump(article_links, outfile, indent=4)

        return penalties
