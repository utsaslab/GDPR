import json
from ..specifications import authority_supported_specification
from ..specifications import eu_member_specification

with open('./gdpr/assets/dba-info.json', 'r') as f:
    supported_dpas = json.load(f)

class DPA(object):
    def __init__(self, iso_code):
        iso_code = iso_code.upper()

        if eu_member_specification.is_satisfied_by(iso_code) is False:
            raise ValueError("iso_code does not belong to a valid eu country member.")

        if authority_supported_specification.is_satisfied_by(iso_code) is False:
            raise ValueError('{iso_code} is not a valid EU member country code.'.format(iso_code=iso_code))

        self.iso_code = iso_code

        dpa = supported_dpas[iso_code]

        self.country = dpa['country']
        self.name = dpa['name']
        self.address = dpa['address']
        self.phone = '({}) {}'.format(dpa['country_code'], dpa['phone'])
        self.email = dpa['email']
        self.website = dpa['website']
        self.member = dpa['member']
        self.sources = dpa['sources']

    def bulk_collect(self, path):
        raise NotImplementedError("Subclasses should implement this function.")
