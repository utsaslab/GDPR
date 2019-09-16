import math
import requests
import json
import pandas as pd
from .models import Penalty
from .policies import gdpr_policy
from .specifications import ico_dataframe_columns_specification
from .services.push_key_service import push_key_service

with open('./modules/gdpr/assets/authorities.json', 'r') as f:
    authorities = json.load(f)

class Authority(object):
    def __init__(self, country_code):
        country_code = country_code.lower()

        if country_code not in authorities.keys():
            raise ValueError('{country_code} is not a valid EU member country code.'.format(country_code=country_code))

        self.country_code = country_code

        self.name = authorities[country_code]["name"]
        self.name_en = authorities[country_code]["name_en"]
        self.short_name = authorities[country_code]["short_name"]
        self.base_url = authorities[country_code]["base_url"]

    def get_penalties(self):
        penalties = []

        if self.country_code == 'uk':
            filename = 'civil-monetary-penalties.xlsx'
            response = requests.get('https://{host}/media/action-weve-taken/csvs/2615397/{filename}'.format(host=self.base_url, filename=filename))

            # important write bytes 'wb'
            with open('./modules/gdpr/assets/' + filename, 'wb') as f:
                f.write(response.content)

            gdpr_implementation_date = gdpr_policy.implementation_date()
            gdpr_implementation_str = gdpr_implementation_date.strftime("%m/%d/%Y")

            df = pd.read_excel('./modules/gdpr/assets/' + filename, sheet_name='civil-monetary-penalties')

            if ico_dataframe_columns_specification.is_satisfied_by(df) is False:
                raise ValueError('Something went wrong during parsing of ' + self.country_code)

            df = df[(df['Date of Final Notice'] >= gdpr_implementation_str)]

            for index, row in df.iterrows():
                # penalty = penalty_factory.create()
                penalty = Penalty(
                    id=push_key_service(Penalty, row['Date of Final Notice'].to_pydatetime(), self.country_code),
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
