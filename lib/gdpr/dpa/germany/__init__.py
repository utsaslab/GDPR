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

from .supervisor.baden_wurttemberg import BadenWurttemberg
from .supervisor.bavaria import Bavaria
from .supervisor.berlin import Berlin

class Germany(DPA):
    def __init__(self):
        iso_code='de'
        super().__init__(iso_code)

    def get_docs(self, path):
        print('docs - dpa germany')
        # BadenWurttemberg().get_docs(path)
        # Bavaria().get_docs(path)
        Berlin().get_docs(path)

        return True
