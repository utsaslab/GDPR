import os
import shutil
import math
import requests
import json
import datetime

from .. import DPA

from bs4 import BeautifulSoup
import dateparser

from ...services.links_from_soup_service import links_from_soup_service
from ...services.filename_from_path_service import filename_from_path_service
from ...services.pdf_to_text_service import pdf_to_text_service

from ...specifications import pdf_file_extension_specification
from ...specifications import page_fully_rendered_specification

from ...modules.pagination import Pagination
from ...policies import bulk_collect_location_policy
from ...policies import filename_length_policy
from ...policies import gdpr_policy

class Belgium(DPA):
    def __init__(self):
        country_code='BE'
        super().__init__(country_code)

    def get_docs(self):
        if bulk_collect_location_policy.is_allowed(self.path) is False:
            raise ValueError('Bulk collect path is illegal: ' + self.path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']
        render_type = source['render_type']

        try:
            response = requests.request('GET', host + start_path)
            html_doc = response.text
            soup = BeautifulSoup(html_doc, 'html.parser')
        except:
            print("oops! something went wrong.")

        pagination = Pagination()
        pagination.add_item(host + start_path)

        pagination_links = links_from_soup_service(soup, target_element=target_element['pagination'])
        for link in pagination_links:
            link_title = link[0]
            link_path = link[1]

            if link_title.isdigit() is False:
                continue

            pagination.add_item(link_path)

        while pagination.has_next():
            page_ref = pagination.get_next()

            if page_fully_rendered_specification.is_satisfied_by(render_type) is False:
                break

            try:
                page_response = requests.request('GET', page_ref)
                html_page = page_response.text
                page_soup = BeautifulSoup(html_page, 'html.parser')
            except:
                print("oops! something went wrong.")

            date_spans = page_soup.find_all('span', class_='date-display-single')
            if date_spans is None or len(date_spans) == 0:
                raise ValueError('Could not determine date_spans')

            root_path = self.path + self.country_code
            result_links = links_from_soup_service(page_soup, target_element=target_element['results'])
            for i in range(len(result_links)):
                result_link = result_links[i]
                date_text = date_spans[i].text
                result_date = dateparser.parse(date_text).date()

                now = datetime.datetime.now()
                gdpr_implementation_date = gdpr_policy.implementation_date()

                if ((result_date.year >= gdpr_implementation_date.year and result_date.month >= gdpr_implementation_date.month) or
                    (result_date.year <= now.year and result_date.month <= now.month)) is False:

                    while pagination.has_next():
                        pagination.get_next()
                    break

                result_title = result_link[0]
                result_path = result_link[1]

                if pdf_file_extension_specification.is_satisfied_by(result_path) is True:
                    pdf_filename = result_title.lower().replace(' ', '-')
                    keepcharacters = ('-')
                    pdf_filename = "".join(c for c in pdf_filename if c.isalnum() or c in keepcharacters).rstrip()

                    if filename_length_policy.is_allowed(pdf_filename) is False:
                        pdf_filename = '-'.join(pdf_filename.split('-')[:10])

                    try:
                        pdf_response = requests.request('GET', result_path)
                    except:
                        print("oops! something went wrong.")

                    dirpath = root_path + '/' + pdf_filename
                    try:
                        os.makedirs(dirpath)
                    except FileExistsError:
                        print('')

                    with open(dirpath + '/original.pdf', 'wb') as f:
                        f.write(pdf_response.content)

                    text = pdf_to_text_service(dirpath + '/original.pdf')
                    with open(dirpath + '/fr.txt', 'w') as f:
                        f.write(text)

            pagination_links = links_from_soup_service(page_soup, target_element=target_element['pagination'])
            for link in pagination_links:
                link_title = link[0]
                link_path = link[1]

                if link_title.isdigit() is False:
                    continue

                pagination.add_item(link_path)

        return True
