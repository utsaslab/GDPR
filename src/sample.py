from modules.gdpr import GDPR

from modules.gdpr.services.pdf_to_text_service import pdf_to_text_service
from modules.gdpr.services.filename_from_path_service import filename_from_path_service
from modules.gdpr.services.dispatch_background_logging_service import dispatch_background_logging_service

from modules.gdpr.services.url_trees_from_sources_service import url_trees_from_sources_service
from modules.gdpr.services.absolute_urls_from_tree_service import absolute_urls_from_tree_service
from modules.gdpr.services.links_from_soup_service import links_from_soup_service

import json
import requests
from bs4 import BeautifulSoup

def main():
    """
    gdpr = GDPR()
    authority = gdpr.get_authority('GB')
    penalties = authority.get_penalties()

    print(penalties)
    for p in penalties:
        print(p.id, p.data_controller + ': ' + p.nature)
    """

    """
    path = './modules/gdpr/assets/r-facebook-mpn-20181024.pdf'
    text = pdf_to_text_service(path)
    filename = filename_from_path_service(path)
    with open('./modules/gdpr/assets/' + filename + '.txt', 'w') as f:
        f.write(text)
    """

    #logpath = '/tmp/gdpr.log'
    #dispatch_background_logging_service(logpath)
    #requests.get('http://httpbin.org/get?foo=bar&baz=python')
    # make sense of log.
    # then delete log after session is over.

    with open('./modules/gdpr/assets/supported_authorities.json', 'r') as f:
        authorities = json.load(f)

    sources = authorities['GB']['sources']

    print("Building source urls as tree(s):")
    root_nodes = url_trees_from_sources_service(sources)
    print(root_nodes)

    print("Extracting absolute urls from the tree(s):")
    for node in root_nodes:
        print(absolute_urls_from_tree_service(node))

print('Extracting links from ico:')

url = 'https://ico.org.uk/action-weve-taken/enforcement?rows=1000000'
response = requests.request('GET', url)
html_doc = response.text

soup = BeautifulSoup(html_doc, 'html.parser')
links = links_from_soup_service(soup, target_element='.resultlist')
print(links)
print('Number of links extracted: {}'.format(len(links)))

if __name__ == '__main__':
    main()
