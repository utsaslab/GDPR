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
from ...specifications import gdpr_retention_specification

from ...modules.pagination import Pagination
from ...policies import bulk_collect_location_policy

class Austria(DPA):
    def __init__(self):
        country_code='AT'
        super().__init__(country_code)

    def get_docs(self): # overwrite=False, to_print=True
        if bulk_collect_location_policy.is_allowed(self.path) is False:
            raise ValueError('Bulk collect path is illegal: ' + self.path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']
        render_type = source['render_type']

        # uncomment to test pagination.
        # start_path = '/Ergebnis.wxe?Abfrage=Dsk&Entscheidungsart=Undefined&Organ=Undefined&SucheNachRechtssatz=True&SucheNachText=True&GZ=&VonDatum=25.08.1991&BisDatum=23.09.2019&Norm=&ImRisSeitVonDatum=&ImRisSeitBisDatum=&ImRisSeit=Undefined&ResultPageSize=100&Suchworte=&Position=1&SkipToDocumentPage=true'
        pagination = Pagination()
        pagination.add_item(host + start_path)

        while pagination.has_next():
            page_url = pagination.get_next()
            results_response = requests.request('GET', page_url)
            results_doc = results_response.text
            results_soup = BeautifulSoup(results_doc, 'html.parser')
            assert results_soup
            table = results_soup.find('table', class_='bocListTable')
            assert table
            tbody = table.find('tbody', class_='bocListTableBody')
            assert tbody
            for tr in tbody.find_all('tr', class_='bocListDataRow'):
                result_index = 2
                date_index = 5
                document_links_index = 9
                td_list = tr.find_all('td', class_='bocListDataCell')
                assert len(td_list) >= max(result_index, date_index + document_links_index) + 1
                date_str = td_list[date_index].get_text()
                tmp = datetime.datetime.strptime('%M/%d/%Y', date_str)
                #print(tmp)
                date = datetime.date(tmp.year, tmp.month, tmp.day)
                if gdpr_retention_specification.is_satisfied_by(date) is False:
                    continue
                result_link = td_list[result_index].find('a')
                assert result_link
                document_title = result_link.get_text()
                document_folder = document_title
                document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                # overwrite determine here.
                # document_folder_md5 not in docs and overwrite == False
                document_links = td_list[document_links_index]
                document_href = None
                for document_link in document_links.find_all('a'):
                    cand_href = document_link.get('href')
                    if cand_href.endswith('.pdf'):
                        document_href = cand_href
                        break
                assert document_href
                #document_href = result_link.get('href')
                document_url = host + document_href

                print("\tdocument_hash:\t", document_folder_md5)

                document_response = requests.request('GET', document_url)
                document_content = document_response.content

                dirpath = root_path + '/' + document_folder_md5
                try:
                    os.makedirs(dirpath)
                except FileExistsError:
                    pass

                # overwrite here.

                with open(dirpath + '/' + language_code + '.pdf', 'wb') as f:
                    f.write(document_content)

                document_text = textract.process(dirpath + '/' + self.language_code + '.pdf')
                with open(dirpath + '/' + language_code + '.txt', 'wb') as f:
                    f.write(document_text)

            pages = result_soup.find('ul', class_='pages')
            if pages is not None:
                for li in pages.find_all('li'):
                    page_link = li.find('a')
                    assert page_link
                    page_href = page_link.get('href')
                    pagination.add_item(host + page_href)

        return True
