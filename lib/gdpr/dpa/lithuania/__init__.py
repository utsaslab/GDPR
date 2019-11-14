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

class Lithuania(DPA):
    def __init__(self):
        country_code='lt'
        super().__init__(country_code)

    def get_docs(self):
        if bulk_collect_location_policy.is_allowed(self.path) is False:
            raise ValueError('Bulk collect path is illegal ' + self.path)

        source = self.sources[0]
        target_element = source['target_element']

        folder_name = self.country.replace(' ', '-').lower()
        root_path = self.path + '/' + folder_name

        export_url = "https://vdai.lrv.lt/lt/naujienos/exportPublicData"
        csv_url = export_url + "?export_data_type=csv&download=1"
        xml_url = export_url + "?export_data_type=xml&download=1"

        now = datetime.datetime.now()
        # document_title = "naujienos-{year}-{month}-{day}".format(year=now.year, month=now.month, day=now.day)
        document_title = "naujienos"
        csv_xml_folder = document_title
        csv_xml_folder_md5 = hashlib.md5(csv_xml_folder.encode()).hexdigest()

        language_code = 'lv'

        dirpath = root_path + '/' + csv_xml_folder_md5
        try:
            os.makedirs(dirpath)
        except FileExistsError:
            print('Directory path already exists, continue.')

        try:
            csv_response = requests.request('GET', csv_url)
            csv_content = csv_response.content

            xml_response = requests.request('GET', xml_url)
            xml_content = xml_response.content
        except:
            print('something went wrong trying to get document')


        with open(dirpath + '/' + language_code + '.csv', 'wb') as f:
            f.write(csv_content)

        with open(dirpath + '/' + language_code + '.xml', 'wb') as f:
            f.write(xml_content)

        with open(dirpath + '/' + language_code + '.csv', encoding="utf-8-sig") as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=";")
            for row in csvreader:
                # eg. 2019-10-24
                date_from = row['date_from']
                tmp = datetime.datetime.strptime(date_from, '%Y-%m-%d')
                date = datetime.date(tmp.year, tmp.month, tmp.day)
                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    continue # try another result_link

                # site = row['site']
                link = row['link']
                document_url = 'https:{path}'.format(path=link)
                print('date, url:\t', date, document_url)

                title = row['title']
                document_folder = title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

                description_html = row['description']
                document_html = BeautifulSoup(description_html, 'html.parser')

                dirpath = root_path + '/' + document_folder_md5
                try:
                    os.makedirs(dirpath)
                except FileExistsError:
                    print('Directory path already exists, continue.')

                document_text = document_html.get_text()

                with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                    f.write(document_text)

        return True
