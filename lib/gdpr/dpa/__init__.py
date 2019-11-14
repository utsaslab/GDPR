import os
import json
from ..specifications import authority_supported_specification
from ..specifications import eu_member_specification
from ..services.translate_price_service import GoogleTranslatePriceService
from google.cloud import translate_v2 as translate

with open('./gdpr/assets/dba-info.json', 'r') as f:
    supported_dpas = json.load(f)

class GoogleTranslatePriceError(Exception):
   """Raised when Google Translate price exceeds a predfined threshold (in usd)."""
   pass

class DPA(object):
    def __init__(self, country_code):
        country_code = country_code.upper()
        if eu_member_specification.is_satisfied_by(country_code) is False:
            raise ValueError("country_code does not belong to a valid eu country member.")
        if authority_supported_specification.is_satisfied_by(country_code) is False:
            raise ValueError('{country_code} is not a valid EU member country code.'.format(country_code=country_code))
        self.country_code = country_code
        dpa = supported_dpas[country_code]
        self.country = dpa['country']
        self.name = dpa['name']
        self.address = dpa['address']
        self.phone = '({}) {}'.format(dpa['phone_code'], dpa['phone'])
        self.email = dpa['email']
        self.website = dpa['website']
        self.member = dpa['member']
        self.sources = dpa['sources']
        self.path = os.getcwd()
        self.translate_client = None

    def set_path(self, path):
        self.path = path

    def set_translate_client(self, translate_client):
        self.translate_client = translate_client

    def get_docs(self):
        raise NotImplementedError("'get_docs' method not implemented.")

    def translate_docs(self, target_languages, docs=[], overwrite=False, price_terminate=0.0, to_print=True):
        if self.translate_client is None:
            self.translate_client = translate.Client()
        target_languages = [lang.lower() for lang in target_languages]
        google_translate_price_service = GoogleTranslatePriceService()
        price = 0.0
        for root,dirs,files in os.walk(self.path + self.country.lower(), topdown=True):
            split = root.split('/')
            is_document_root = split.index(self.country.lower()) < len(split) - 1
            if is_document_root:
                doc = split[-1]
                if len(docs) == 0 or doc in docs:
                    for name in files:
                        if name.endswith('.txt') == False:
                            continue
                        language = name.split('.')[0]
                        if language in target_languages and overwrite != True:
                            continue
                        if price_terminate > 0.0 and price >= price_terminate:
                            raise GoogleTranslatePriceError(f"Estimated price of Google Translate exceeded value of {price_terminate}.")
                        with open(root + '/' + name, 'r', encoding='utf-8') as f:
                            document_text = f.read()
                            for target_language in target_languages:
                                response = None
                                try:
                                    response = self.translate_client.translate(document_text, target_language=target_language)
                                except ValueError:
                                    # pass
                                    raise ValueError('Something went wrong.')
                                translated_text = response['translatedText']
                                with open(root + '/' + target_language + '.txt', 'w') as outfile:
                                    outfile.write(translated_text)
                                price += google_translate_price_service.price_for_text(document_text)
                                if to_print:
                                    print('doc:', doc)
                                    print('\tfile:', name)
                                    print('\tprice:', price)
        return True
