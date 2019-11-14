import os
import shutil
import math
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

from .. import DPA

from ...services.links_from_soup_service import links_from_soup_service
from ...specifications import pdf_file_extension_specification
from ...specifications import page_fully_rendered_specification

from ...policies import gdpr_policy
from .services.filter_dataframe_pre_gdpr_service import filter_dataframe_pre_gdpr_service
from ...services.pdf_to_text_service import pdf_to_text_service

class UnitedKingdom(DPA):
    def __init__(self):
        country_code='GB'
        super().__init__(country_code)

    def get_docs(self):

        spreadsheet = self.sources[0]
        host = spreadsheet['host']
        start_path = spreadsheet['start_path']

        filename = start_path.split('/')[-1]
        response = requests.request('GET', host + start_path)

        with open('/tmp/' + filename, 'wb') as f:
            f.write(response.content)

        df = pd.read_excel('/tmp/' + filename, sheet_name='civil-monetary-penalties')

        gdpr_implementation_date = gdpr_policy.implementation_date()
        df = filter_dataframe_pre_gdpr_service(df, gdpr_implementation_date)

        root_path = self.path + self.country_code
        dirpath = root_path
        try:
            os.makedirs(dirpath)
        except FileExistsError:
            print('file already exists, continue.')

        df.to_csv(dirpath + '/' + filename.split('.')[0] + '.csv')
        shutil.rmtree('/tmp/' + filename, ignore_errors=True)

        website = self.sources[1]
        website_host = website['host']
        website_start_path = website['start_path']
        website_target_element = website['target_element']

        try:
            website_response = requests.request('GET', website_host + website_start_path)
            website_html = website_response.text
            website_soup = BeautifulSoup(website_html, 'html.parser')
        except:
            print('Timeout session occurred.')

        root_path = self.path + self.country_code

        result_links = links_from_soup_service(website_soup, target_element=website_target_element['results'])
        for link in result_links:
            result_title = link[0]
            result_path = link[1]
            try:
                document_response = requests.request('GET', website_host + result_path)
                document_html = document_response.text

                document_soup = BeautifulSoup(document_html, 'html.parser')
            except:
                print('Timeout session occurred.')


            document_links = links_from_soup_service(document_soup, target_element=website_target_element['document'])
            for doclink in document_links:
                doctitle = doclink[0]
                docpath = doclink[1]
                if pdf_file_extension_specification.is_satisfied_by(docpath) is True:
                    doc_response = requests.request('GET', website_host + docpath)

                    document_filename = doctitle.lower().replace(' ', '-')
                    keepcharacters = ('-','.','_')
                    document_filename = "".join(c for c in document_filename if c.isalnum() or c in keepcharacters).rstrip()

                    dirpath = root_path + '/' + document_filename
                    try:
                        os.makedirs(dirpath)
                    except FileExistsError:
                        print('file already exists, continue.')

                    with open(dirpath + '/original.pdf', 'wb') as f:
                        f.write(doc_response.content)

                    text = pdf_to_text_service(dirpath + '/original.pdf')
                    with open(dirpath + '/' + self.country_code.lower() + '.txt', 'w') as f:
                        f.write(text)


        return True
