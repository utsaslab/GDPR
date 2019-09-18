from modules.gdpr import GDPR

from modules.gdpr.services.pdf_to_text_service import pdf_to_text_service
from modules.gdpr.services.filename_from_path_service import filename_from_path_service

def main():
    gdpr = GDPR()
    authority = gdpr.get_authority('GB')
    penalties = authority.get_penalties()

    print(penalties)
    for p in penalties:
        print(p.id, p.data_controller + ': ' + p.nature)

    """path = './modules/gdpr/assets/r-facebook-mpn-20181024.pdf'
    text = pdf_to_text_service(path)
    filename = filename_from_path_service(path)
    with open('./modules/gdpr/assets/' + filename + '.txt', 'w') as f:
        f.write(text)"""

if __name__ == '__main__':
    main()
