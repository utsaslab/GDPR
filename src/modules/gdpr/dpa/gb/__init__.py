import os
import shutil
import math
import requests
import json
import pandas as pd

from .. import DPA

from ...policies import gdpr_policy
from .services.filter_dataframe_pre_gdpr_service import filter_dataframe_pre_gdpr_service

class GB(DPA):
    def __init__(self):
        iso_code='GB'
        super().__init__(iso_code)

    def bulk_collect(self, path):
        penalties = []

        source = self.sources[0]
        host = source['host']
        start_path = source['start_path']

        filename = start_path.split('/')[-1]
        response = requests.request('GET', host + start_path)

        with open('/tmp/' + filename, 'wb') as f:
            f.write(response.content)

        df = pd.read_excel('/tmp/' + filename, sheet_name='civil-monetary-penalties')

        gdpr_implementation_date = gdpr_policy.implementation_date()
        df = filter_dataframe_pre_gdpr_service(df, gdpr_implementation_date)

        root_path = path + self.iso_code
        dirpath = root_path
        try:
            os.makedirs(dirpath)
        except FileExistsError:
            print('file already exists, continue.')

        df.to_csv(dirpath + '/' + filename.split('.')[0] + '.csv')
        shutil.rmtree('/tmp/' + filename, ignore_errors=True)

        return True
