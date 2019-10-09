import os
import math
import requests
import json
import datetime
import hashlib
import dateparser

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

from .policies import rtf_decoding_policy
from striprtf.striprtf import rtf_to_text

class France(DPA):
    def __init__(self):
        iso_code='FR'
        super().__init__(iso_code)

    def bulk_collect(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']
        render_type = source['render_type']

        pagination = Pagination()
        pagination.add_link(host + start_path)
        # restart at page: 173
        # https://www.legifrance.gouv.fr/rechExpCnil.do;jsessionid=C2ACB9BBE6A225D186181BDAC22A13CD.tplgfr41s_3?reprise=true&fastReqId=1068661056&page=173
        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        while pagination.has_next():
            page_url = pagination.get_next()
            print('Bulk collection this page:', page_url)
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

                    document_folder = result_title
                    document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

                    language_code = 'fr'

                    content_element = document_soup.find(id=target_element['date'].split('#')[-1])
                    content_text = content_element.get_text()

                    # Example: ['Etat: VIGUEUR', 'Nature de la délibération: AUTORISATION RECHERCHE', 'Date de la publication sur legifrance: 11 avril 2014']
                    content_elements = list(filter(None, content_text.strip(" ").split('\n')))[-1]
                    date_str = content_elements.split(':')[-1].strip(' ')
                    tmp = dateparser.parse(date_str, languages=[language_code])
                    date = datetime.date(tmp.year, tmp.month, tmp.day)

                    if gdpr_retention_specification.is_satisfied_by(date) is False:
                        continue # try another result_link

                    print(document_folder_md5)
                    dirpath = root_path + '/' + document_folder_md5
                    try:
                        os.makedirs(dirpath)
                    except FileExistsError:
                        print('Directory path already exists, continue.')

                    document_links = links_from_soup_service(document_soup, target_element=target_element['document'])
                    if len(document_links) > 1:
                        raise ValueError('Something went wrong.')

                    rtf_link = document_links[0][1]
                    rtf_response = requests.request('GET', host + '/' + rtf_link)
                    rtf_content = rtf_response.content

                    with open(dirpath + '/' + language_code + '.rtf', 'wb') as f:
                        f.write(rtf_content)

                    text = rtf_to_text(
                        rtf_content.decode(rtf_decoding_policy.decode())
                    )

                    with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                        f.write(text)


                except:
                    print("Something went wrong.")

            pagination_links = links_from_soup_service(results_soup, target_element=target_element['pagination'])
            for pagination_link in pagination_links:
                page_url = pagination_link[1]
                pagination.add_link(host + page_url)

        return True
