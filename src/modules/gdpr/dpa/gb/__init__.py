from .. import DPA

import math
import requests
import json
import pandas as pd

from ...policies import gdpr_policy
from ...specifications import gb_dataframe_columns_specification
from ...services.gb_filter_rows_pre_gdpr_service import gb_filter_rows_pre_gdpr_service
from ...factories import penalty_factory

class GB(DPA):
    def __init__(self):
        iso_code='GB'
        super().__init__(iso_code)

    def bulk_collect(self, path):
        penalties = []

        filename = 'civil-monetary-penalties.xlsx'
        response = requests.get('https://{host}/media/action-weve-taken/csvs/2615397/{filename}'.format(host=self.base_url, filename=filename))

        # important write bytes 'wb'
        with open('./modules/gdpr/assets/' + filename, 'wb') as f:
            f.write(response.content)

        df = pd.read_excel('./modules/gdpr/assets/' + filename, sheet_name='civil-monetary-penalties')

        if gb_dataframe_columns_specification.is_satisfied_by(df) is False:
            raise ValueError('Something went wrong during parsing of ' + self.iso_code)

        gdpr_implementation_date = gdpr_policy.implementation_date()
        df = gb_filter_rows_pre_gdpr_service(df, gdpr_implementation_date)

        for index, row in df.iterrows():
            penalty = penalty_factory.create(
                iso_code=self.iso_code,
                data_controller=row['Data Controller'],
                sector=row['Sector '],
                nature=row['Nature'],
                date=row['Date of Final Notice'].to_pydatetime(),
                fine=row['DPA fine '] if math.isnan(row['DPA fine ']) != True else row['PECR fine '],
                currency='gbp',
                notes=row['Notes']
            )
            penalties.append(penalty)

        return penalties
