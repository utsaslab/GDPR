import os
import math
import requests
import json
import datetime

from .. import DPA

from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector

from ...services.links_from_soup_service import links_from_soup_service
from ...services.filename_from_path_service import filename_from_path_service
from ...services.pdf_to_text_service import pdf_to_text_service

from ...specifications import pdf_file_extension_specification
from ...specifications import page_fully_rendered_specification

from ...modules.pagination import Pagination
from ...policies import bulk_collect_location_policy
from ...policies import gdpr_policy

from urllib.parse import urlparse

class Bulgaria(DPA):
    def __init__(self):
        country_code='BG'
        super().__init__(country_code)

    def get_docs(self):
        if bulk_collect_location_policy.is_allowed(self.path) is False:
            raise ValueError('Bulk collect path is illegal: ' + self.path)

        for source in self.sources:
            source_host = source['host']
            source_start_path = source['start_path']
            source_target_element = source['target_element']
            source_render_type = source['render_type']

            try:
                source_response = requests.request('GET', source_host + source_start_path)
                source_html = source_response.text
                source_soup = BeautifulSoup(source_html, 'html.parser')
            except:
                print('Timeout session occurred.')

            pagination = Pagination()
            pagination.add_item("{host}{path}".format(host=source_host, path=source_start_path))

            pagination_links = links_from_soup_service(source_soup, target_element=source_target_element['pagination'])
            for link in pagination_links:
                title = link[0]
                link_path = link[1]
                if title.isdigit() is False:
                    continue

                pagination.add_item(source_host + link_path)

            while pagination.has_next():
                results_page = pagination.get_next()

                try:
                    results_response = requests.request('GET', results_page)
                    results_html = results_response.content
                    results_soup = BeautifulSoup(results_html, 'html.parser')
                except:
                    print('Timeout session occurred.')

                result_2019_links = links_from_soup_service(results_soup, target_element=source_target_element['results'])
                for link in result_2019_links:
                    title = link[0]
                    query = link[1]
                    url = "{host}{path}{query}".format(host=source_host, path=source_start_path.split('?')[0], query=query)
                    o = urlparse(url)

                    if len(o.query) == 0:
                        continue

                    query = {}
                    for param in o.query.split('&'):
                        param_split = param.split('=')
                        query[param_split[0]] = param_split[1]

                    if 'p' not in query.keys() or query['p'] != 'element_view':
                        continue

                    try:
                        document_response = requests.request('GET', url)
                        document_html = document_response.content
                        document_soup = BeautifulSoup(document_html, 'html.parser')
                    except:
                        print('Timeout session occurred.')

                    target_area = document_soup.find('div', class_='center-part')
                    if target_area is None:
                        continue

                    document_links = links_from_soup_service(document_soup, target_element=source_target_element['document'])
                    for doc_link in document_links:
                        doc_link_url = doc_link[1]
                        if doc_link_url.startswith('download.php') is False:
                            continue

                        try:
                            doc_response = requests.request('GET', source_host + '/' + doc_link_url)
                        except:
                            print('Timeout session occurred.')

                        root_path = self.path
                        dirpath = root_path + '/' + self.country_code + '/' + query['aid']

                        try:
                            os.makedirs(dirpath)
                        except FileExistsError:
                            print('file already exists, continue.')

                        with open(dirpath + '/original.pdf', 'wb') as f:
                            f.write(doc_response.content)

                        try:
                            document_text = pdf_to_text_service(dirpath + '/original.pdf')
                        except:
                            print('Oops. PDF conversion went wrong.')

                        with open(dirpath + '/' + self.country_code.lower() + '.txt', 'w') as f:
                            f.write(document_text)

                        break # there's only one pdf respective to each document

        return True
