import json
from ..specifications import authority_supported_specification
from ..specifications import eu_member_specification

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
        raise NotImplementedError("Subclasses should implement this function.")
