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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ...policies import webdriver_executable_path_policy

class Spain(DPA):
    def __init__(self):
        iso_code='es'
        super().__init__(iso_code)

    def get_docs(self, path):
        if bulk_collect_location_policy.is_allowed(path) is False:
            raise ValueError('Bulk collect path is illegal ' + path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        language_code = 'es'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = path + '/' + folder_name

        source_url = host + start_path

        exec_path = webdriver_executable_path_policy.path_for_system()

        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        driver = webdriver.Chrome(options=options, executable_path=exec_path)
        driver.get(source_url)
        try:
            WebDriverWait(driver, 60).until_not(
                EC.presence_of_element_located((By.ID, "loading"))
            )

            page_source = driver.page_source
            source_soup = BeautifulSoup(page_source, 'html.parser')

            cursor = 0
            while cursor > -1:
                print('page:\t', cursor)
                if cursor == 0:
                    driver.get(source_url)
                else:
                    try:
                         pager = driver.find_element_by_class_name('pager')
                         next_button = pager.find_elements_by_tag_name('a')[-1]
                         next_button.click()
                    except:
                         cursor = -1
                         break
                cursor += 1

                try:
                    WebDriverWait(driver, 60).until_not(
                        EC.presence_of_element_located((By.ID, "loading"))
                    )

                    results_source = driver.page_source
                    results_soup = BeautifulSoup(results_source, 'html.parser')

                    items_list = results_soup.find('ul', class_='items-list')
                    if items_list is None:
                        return True

                    for li in items_list.find_all('li', class_='page'):
                        section_body = li.find('section', class_='body')
                        if section_body is None:
                            return True

                        h4 = section_body.find('h4')
                        if h4 is None:
                            return True

                        a = h4.find('a')
                        if a is None:
                            return True

                        document_title = a.get_text()
                        document_folder = document_title
                        document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()

                        document_href = a.get('href')

                        now = datetime.datetime.now()
                        gdpr_date = gdpr_policy.implementation_date()

                        date_cand = int(document_title.split('-')[-1].split('_')[0])
                        if date_cand < gdpr_date.year or date_cand > now.year:
                            return True # should be continue

                        if document_href.endswith('.pdf') is False:
                            continue

                        print("\tdocument_hash:\t", document_folder_md5)
                        document_url = host + document_href
                        document_response = requests.request('GET', document_url)
                        document_content = document_response.content

                        dirpath = root_path + '/' + document_folder_md5
                        try:
                            os.makedirs(dirpath)

                            with open(dirpath + '/' + language_code + '.pdf', 'wb') as f:
                                f.write(document_content)

                            document_text = textract.process(dirpath + '/' + language_code + '.pdf')
                            with open(dirpath + '/' + language_code + '.txt', 'wb') as f:
                                f.write(document_text)

                        except FileExistsError:
                            print('Directory path already exists, continue.')
                except:
                    print('something went wrong with the driver.')

        finally:
            driver.quit()
        return True
