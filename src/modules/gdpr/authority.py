import math
import requests
import json
import pandas as pd

from .policies import gdpr_policy

from .specifications import gb_dataframe_columns_specification
from .specifications import authority_supported_specification
from .specifications import eu_member_specification

from .services.gb_filter_rows_pre_gdpr_service import gb_filter_rows_pre_gdpr_service

from .factories import penalty_factory

with open('./modules/gdpr/assets/supported_authorities.json', 'r') as f:
    authorities = json.load(f)

class Authority(object):
    def __init__(self, country_code):
        country_code = country_code.upper()

        if eu_member_specification.is_satisfied_by(country_code) is False:
            raise ValueError("country code does not belong to a valid eu country member.")

        if authority_supported_specification.is_satisfied_by(country_code) is False:
            raise ValueError('{country_code} is not a valid EU member country code.'.format(country_code=country_code))

        self.country_code = country_code

        self.name = authorities[country_code]["name"]
        self.name_en = authorities[country_code]["name_en"]
        self.short_name = authorities[country_code]["short_name"]
        self.base_url = authorities[country_code]["base_url"]

    def get_penalties(self):
        penalties = []

        if self.country_code == 'GB':
            filename = 'civil-monetary-penalties.xlsx'
            response = requests.get('https://{host}/media/action-weve-taken/csvs/2615397/{filename}'.format(host=self.base_url, filename=filename))

            # important write bytes 'wb'
            with open('./modules/gdpr/assets/' + filename, 'wb') as f:
                f.write(response.content)

            df = pd.read_excel('./modules/gdpr/assets/' + filename, sheet_name='civil-monetary-penalties')

            if gb_dataframe_columns_specification.is_satisfied_by(df) is False:
                raise ValueError('Something went wrong during parsing of ' + self.country_code)

            gdpr_implementation_date = gdpr_policy.implementation_date()
            df = gb_filter_rows_pre_gdpr_service(df, gdpr_implementation_date)

            for index, row in df.iterrows():
                penalty = penalty_factory.create(
                    country_code=self.country_code,
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
