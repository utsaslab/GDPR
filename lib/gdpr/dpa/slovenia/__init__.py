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

class Slovenia(DPA):
    def __init__(self):
        country_code='si'
        super().__init__(country_code)

    def get_docs(self):
        if bulk_collect_location_policy.is_allowed(self.path) is False:
            raise ValueError('Bulk collect path is illegal ' + self.path)

        source = self.sources[0]

        host = source['host']
        start_path = source['start_path']
        target_element = source['target_element']

        language_code = 'sl'

        folder_name = self.country.replace(' ', '-').lower()
        root_path = self.path + '/' + folder_name

        source_url = host+start_path

        # Download stable version of ChromeDriver
        # https://chromedriver.storage.googleapis.com/index.html?path=78.0.3904.70/
        # make service that can generate path to exe for sys version running
        exec_path = webdriver_executable_path_policy.path_for_system()

        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        driver = webdriver.Chrome(options=options, executable_path=exec_path)
        driver.get(source_url)
        try:
            source_element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, "scheme5"))
            )

            page_source = source_element.get_attribute('innerHTML') # driver.page_source # a str.
            source_soup = BeautifulSoup(page_source, 'html.parser')

            paginator = source_soup.find('ul', class_='f3-widget-paginator')
            if paginator is None:
                return True

            pagination = Pagination()
            pagination.add_item(source_url)

            for li in paginator.find_all('li'):
                a = li.find('a')
                if a is None:
                    continue
                href = a.get('href')
                pagination.add_item(href)

            while pagination.has_next():
                page_url = pagination.get_next()
                print('page_url:', page_url)

                driver.get(page_url)
                try:
                    page_element = WebDriverWait(driver, 60).until(
                        EC.presence_of_element_located((By.ID, "scheme5"))
                    )

                    results_source = page_element.get_attribute('innerHTML')
                    results_soup = BeautifulSoup(results_source, 'html.parser')

                    news_small = results_soup.find('ul', class_='news-small')
                    for li in news_small.find_all('li'):
                        a = li.find('a')
                        if a is None:
                            return True

                        time = a.find('time')
                        if time is None:
                            return True

                        date_str = time.get('datetime') # time.get_text()
                        if datetime is None:
                            return True

                        # eg. 22.10.2019
                        tmp = datetime.datetime.strptime(date_str, '%d.%m.%Y')
                        date = datetime.date(tmp.year, tmp.month, tmp.day)

                        if gdpr_retention_specification.is_satisfied_by(date) is False:
                            continue # try another result_link # should be continue

                        strong = a.find('strong')
                        if strong is None:
                            return True

                        document_title = strong.get_text()
                        document_folder = document_title
                        document_folder_md5 = hashlib.md5(document_folder.encode()).hexdigest()
                        print("\tdocument_hash:\t", document_folder_md5)

                        document_href = a.get('href')
                        document_url = document_href

                        driver.get(document_url)
                        try:
                            document_element = WebDriverWait(driver, 60).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "article"))
                            )

                            document_source = document_element.get_attribute('innerHTML')
                            document_soup = BeautifulSoup(document_source, 'html.parser')

                            document_text = ""
                            for body_text in document_soup.find_all('p', class_='bodytext'):
                                document_text += body_text.get_text()

                            if len(document_text) == 0:
                                return True

                            dirpath = root_path + '/' + document_folder_md5
                            try:
                                os.makedirs(dirpath)
                                with open(dirpath + '/' + language_code + '.txt', 'w') as f:
                                    f.write(document_text)
                            except FileExistsError:
                                print('Directory path already exists, continue.')
                        except:
                            print('something went wrong with the driver.')
                except:
                    print('something went wrong with the driver.')
        finally:
            driver.quit()

        return True
