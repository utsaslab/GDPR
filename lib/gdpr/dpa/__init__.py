import os
import json
import time
from ..specifications import authority_supported_specification
from ..specifications import eu_member_specification
from ..services.google_translate_price_service import GoogleTranslatePriceService
from ..services.google_translate_quota_limit_service import GoogleTranslateQuotaLimitService
from ..services.target_languages_service import TargetLanguagesService
from ..specifications.document_root_specification import DocumentRootSpecification
from ..services.document_languages_service import DocumentLanguagesService
from ..policies.translate_file_format_policy import TranslateFileFormatPolicy
from ..specifications.price_terminate_translate_specification import PriceTerminateTranslateSpecification
from ..specifications.exceeded_daily_translate_quota_limit_specification import ExceededDailyTranslateQuotaLimitSpecification
from ..specifications.translate_100_secs_quota_spec import Translate100SecsQuotaSpec
from ..specifications.translate_document_specification import TranslateDocumentSpecification
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

    def translate_docs(self, target_languages, docs=[], overwrite=False, price_terminate_usd=0.0, quota_limit_service=None, to_print=True):
        target_languages = TargetLanguagesService(self).filter_target_languages(target_languages)
        if self.translate_client is None:
            self.translate_client = translate.Client()
        price_service = GoogleTranslatePriceService()
        if quota_limit_service is None:
            quota_limit_service = GoogleTranslateQuotaLimitService()
        price = 0.0
        quota_limit = 0
        time_window_secs = 100
        for root,dirs,files in os.walk(self.path + self.country.lower(), topdown=True):
            split = root.split('/')
            doc = split[-1]
            if DocumentRootSpecification(self).is_satisfied_by(root) is False:
                continue
            if TranslateDocumentSpecification(docs).is_satisfied_by(doc) is False:
                continue
            document_languages = DocumentLanguagesService(files).get()
            for name in files:
                if TranslateFileFormatPolicy().is_file_allowed(name) is False:
                    continue
                if PriceTerminateTranslateSpecification(price_terminate_usd).is_satisfied_by(price):
                    raise GoogleTranslatePriceError(f"Estimated price of Google Translate exceeded value of {price_terminate_usd}.")
                with open(root + '/' + name, 'r', encoding='utf-8') as f:
                    document_text = f.read()
                    if ExceededDailyTranslateQuotaLimitSpecification(quota_limit_service).is_satisfied_by(quota_limit + len(document_text)):
                        raise ValueError('Reached characters per day: %d. Please wait 24 hours until making another request.', quota)
                    if Translate100SecsQuotaSpec(quota_limit_service).is_satisfied_by(
                        quota_limit + len(document_text)
                    ):
                        if to_print:
                            print('Reached characters per 100 seconds per project per user: %d. sleeping %d secs before making next request.' % (quota_limit, time_window_secs))
                        time.sleep(time_window_secs+5)
                        quota_limit = 0
                    for target_language in target_languages:
                        if target_language in document_languages and overwrite == False:
                            continue
                        response = None
                        try:
                            response = self.translate_client.translate(document_text, target_language=target_language)
                        except:
                            #pass
                            raise ValueError('Something went wrong.')
                        translated_text = response['translatedText']
                        with open(root + '/' + target_language + '.txt', 'w') as outfile:
                            outfile.write(translated_text)
                        price += price_service.price_for_text(document_text)
                        quota_limit += len(document_text)
                        if to_print:
                            print('doc:', doc)
                            print('\tfile:', name)
                            print('\tprice:', price)
        return True

    def classify_docs():
        # source: https://medium.com/moosend-engineering-data-science/how-to-build-a-machine-learning-industry-classifier-5d19156d692f
        return True
