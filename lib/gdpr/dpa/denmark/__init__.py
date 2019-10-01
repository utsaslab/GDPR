import os
import math
import requests
import json
import datetime

from .. import DPA

from bs4 import BeautifulSoup

from ...services.links_from_soup_service import links_from_soup_service
from ...services.filename_from_path_service import filename_from_path_service
from ...services.pdf_to_text_service import pdf_to_text_service

from ...specifications import pdf_file_extension_specification
from ...specifications import page_fully_rendered_specification

from ...modules.pagination import Pagination
from ...policies import bulk_collect_location_policy
from ...policies import gdpr_policy

class Denmark(DPA):
    def __init__(self):
        iso_code='DK'
        super().__init__(iso_code)

    def bulk_collect(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal: ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']
        render_type = source['render_type']

        now = datetime.datetime.now()
        gdpr_implementation_date = gdpr_policy.implementation_date()

        year_range = range(gdpr_implementation_date.year, now.year+1)
        month_range = range(1, 12+1)

        pagination = Pagination()
        for year in year_range:
            for month in month_range:
                if year == now.year and month > now.month:
                    continue

                if year == gdpr_implementation_date.year and month < gdpr_implementation_date.month:
                    continue

                link = "/tilsyn-og-afgoerelser/afgoerelser/?year={year}&month={month}".format(year=year, month=month)
                pagination.add_link(link)

        while(pagination.has_next()):
            page_ref = pagination.get_next()

            if page_fully_rendered_specification.is_satisfied_by(render_type) is False:
                break

            try:
                response = requests.request('GET', host + page_ref)
                html_doc = response.text
                _soup = BeautifulSoup(html_doc, 'html.parser')
            except:
                print('Timeout session occurred.')

            root_path = path + self.iso_code
            result_links = links_from_soup_service(_soup, target_element=target_element['results'])
            for link in result_links:
                title = link[0]
                _path = link[1]

                document_filename = title.lower().replace(' ', '-')
                keepcharacters = ('-','.','_')
                document_filename = "".join(c for c in document_filename if c.isalnum() or c in keepcharacters).rstrip()

                try:
                    document_response = requests.request('GET', host + _path)
                    document_html = document_response.text

                    document_soup = BeautifulSoup(document_html, 'html.parser')
                except:
                    print('Timeout session occurred.')

                # NOTE: (make service): text_from_soup_service(soup, target_element)
                target_area = document_soup.find('div', class_=target_element['document'].split('.')[-1])
                document_text = target_area.get_text()

                dirpath = root_path + '/' + document_filename
                try:
                    os.makedirs(dirpath)
                except FileExistsError:
                    print('file already exists, continue.')

                with open(dirpath + '/da.txt', 'w') as f:
                    f.write(document_text)

        return True
