import os
import json
import time
from ..specifications import authority_supported_specification
from ..specifications import eu_member_specification
from ..services.translate_price_service import TranslatePriceService
from ..services.translate_quota_service import TranslateQuotaService
from ..specifications.document_root_spec import DocumentRootSpec
from ..services.files_languages_service import FilesLanguagesService
from ..policies.translate_file_policy import TranslateFilePolicy
from ..specifications.price_terminate_translate_specification import PriceTerminateTranslateSpecification
from ..specifications.not_reached_daily_translate_quota_spec import NotReachedDailyTranslateQuotaSpec
from ..specifications.not_reached_100_secs_translate_quota_specs import NotReached100SecsTranslateQuotaSpecs
from ..specifications.translate_document_spec import TranslateDocumentSpec
from ..specifications.exists_file_language_spec import ExistsFileLanguageSpec
from google.cloud import translate_v2 as translate
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
nltk.download('punkt')
nltk.download('stopwords')

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
        self.language_code = dpa['language_code']
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

    def translate_docs(self, target_languages, docs=[], overwrite=False, price_terminate_usd=0.0, quota_service=None, to_print=True):
        target_languages = list(set(target_languages).difference(self.language_code))
        if self.translate_client is None:
            self.translate_client = translate.Client()
        price_service = TranslatePriceService()
        if quota_service is None:
            quota_service = TranslateQuotaService()
        agg_price = 0.0
        agg_quota = 0
        time_window_secs = 100
        for root,dirs,files in os.walk(self.path + self.country.lower(), topdown=True):
            doc = root.split('/')[-1]
            if DocumentRootSpec(doc).is_satisfied_by(root) is False:
                continue
            if TranslateDocumentSpec(docs).is_satisfied_by(doc) is False:
                continue
            file_languages = FilesLanguagesService(files).get_languages()
            for name in files:
                if TranslateFilePolicy().is_allowed(name) is False:
                    continue
                if PriceTerminateTranslateSpec(price_terminate_usd).is_satisfied_by(agg_price):
                    raise GoogleTranslatePriceError(f"Estimated price of Google Translate exceeded value of {price_terminate_usd}.")
                with open(root + '/' + name, 'r', encoding='utf-8') as f:
                    document_text = f.read()
                    next_quota = agg_quota + len(document_text)
                    if NotReachedDailyTranslateQuotaSpec(quota_service).is_satisfied_by(next_quota) is False:
                        raise ValueError('Reached characters per day: %d. Please wait 24 hours until making another request.', agg_quota)
                    if NotReached100SecsTranslateQuotaSpecs(quota_service).is_satisfied_by(next_quota) is False:
                        if to_print:
                            print('Reached characters per 100 seconds per project per user: %d. sleeping %d secs before making next request.' % (agg_quota, time_window_secs))
                        time.sleep(time_window_secs+5)
                        agg_quota = 0
                    for target_language in target_languages:
                        if overwrite == False or ExistsFileLanguageSpec(file_languages).is_satisfied_by(target_language) is False:
                            continue
                        response = None
                        try:
                            # provide source of the dpa.
                            response = self.translate_client.translate(document_text, target_language=target_language)
                        except:
                            #pass
                            raise ValueError('Something went wrong.')
                        translated_text = response['translatedText']
                        with open(root + '/' + target_language + '.txt', 'w') as outfile:
                            outfile.write(translated_text)
                        agg_price += price_service.price_for_text(document_text)
                        agg_quota += len(document_text)
                        if to_print:
                            print('doc:', doc)
                            print('\tfile:', name)
                            print('\tprice:', price)
        return True

    def classify_docs(self, docs=[]):
        # source: https://medium.com/moosend-engineering-data-science/how-to-build-a-machine-learning-industry-classifier-5d19156d692f
        corpus = []
        doc_words = {}
        stopwords_ = set(stopwords.words('english')) # english
        ps = PorterStemmer()
        root = 0
        #for country in ['italy', 'slovenia', 'ireland', 'denmark']:
        for country in ['austria']:
            for root,dirs,files in os.walk('../data/09-25-2019/' + country, topdown=True): # self.path + self.country.lower()
                split = root.split('/')
                doc = split[-1]
                #if DocumentRootSpec(self).is_satisfied_by(root) is False:
                #    continue
                if root == 0:
                    root += 1
                    continue
                for name in files:
                    if name.startswith('en') is False:
                        continue
                    if name.endswith('.txt') is False:
                        continue
                    with open(root + '/' + name, 'r', encoding='utf-8') as f:
                        #doc_text = f.read()
                        #corpus.append(doc_text)
                        text = f.read()
                        words = nltk.word_tokenize(text)
                        words = [word for word in words if word not in ['.', ',', '(', ')', '#', '[', ']', '=', ':', '?', '{', '}', '&']] # or just not in the alphabet regexp.
                        words = [word for word in words if word not in stopwords_]
                        print(json.dumps(Counter(words).most_common(), indent=4))
                        words = [ps.stem(word) for word in words] # list(set())
                        doc_text = ' '.join(words)
                        corpus.append(doc_text)
                root = 0
        # BOW approach
        """vectorizer = CountVectorizer(lowercase=True, stop_words='english')
        X = vectorizer.fit_transform(corpus)
        print(vectorizer.get_feature_names())
        print(X.toarray())"""

        # TD-idf
        """vectorizer = TfidfVectorizer()
        Xo = vectorizer.fit_transform(corpus)
        print(vectorizer.get_feature_names())
        print(Xo.toarray())
        df = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names())
        print(df)
        #ax1 = df.plot
        #plt.scatter(df[:,0], df[:,1], c=df.target)
        #plt.show()
        #print(json.dumps(doc_words, indent=4))"""

        from sklearn.datasets import fetch_20newsgroups
        from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
        from sklearn.decomposition import PCA
        from sklearn.pipeline import Pipeline
        from sklearn.cluster import KMeans
        import matplotlib.pyplot as plt

        newsgroups_train = corpus

        pipeline = Pipeline([
            ('vect', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
        ])
        X = pipeline.fit_transform(newsgroups_train).todense()

        pca = PCA(n_components=2).fit(X)
        data2D = pca.transform(X)
        kmeans = KMeans(n_clusters=2).fit(X)
        centers2D = pca.transform(kmeans.cluster_centers_)

        plt.scatter(data2D[:,0], data2D[:,1], c=kmeans.labels_.tolist())
        #plt.show()              #not required if using ipython notebook


        plt.scatter(centers2D[:,0], centers2D[:,1],
                    marker='x', s=200, linewidths=3, c='r')
        plt.show()              #not required if using ipython notebook

        return True
