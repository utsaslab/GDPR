import os
import io
import shutil
from pdfminer.converter import TextConverter
from pdfminer.converter import PDFPageAggregator

from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager

from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTImage, LTFigure

from pdf2image import convert_from_path
from PIL import Image # brew install pillow
from pytesseract import image_to_string # brew install tesseract

from ..specifications import pdf_file_extension_specification
from ..specifications import doc_is_full_specification
from .filename_from_path_service import filename_from_path_service

TMP_PATH = '/tmp'

# subroutine
def pdf_images_to_text(path):
    if pdf_file_extension_specification.is_satisfied_by(path) is False:
        raise ValueError("path is not of type pdf")

    pages = convert_from_path(path, 500)

    if doc_is_full_specification.is_satisfied_by(pages) is False:
        return None

    filename = filename_from_path_service(path)
    dirpath = TMP_PATH + '/' + filename

    try:
        os.makedirs(dirpath)
        #os.mkdir(dirpath)
    except FileExistsError:
        print("directory already exists.")

    text = ''
    for i in range(len(pages)):
        im_path = '{path}/{no}.jpg'.format(path=dirpath, no=i)

        page = pages[i]
        page.save(im_path, 'JPEG')

        im = Image.open(im_path)
        text += image_to_string(im, lang='eng')

        if i != len(pages) - 1:
            text += '\n'

    shutil.rmtree(dirpath, ignore_errors=True)

    text = text.strip()
    return text

def pdf_to_text_service(path):
    if pdf_file_extension_specification.is_satisfied_by(path) is False:
        raise ValueError("path is not of type pdf")

    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    text = text.strip()

    if doc_is_full_specification.is_satisfied_by(text) is False:
        text = pdf_images_to_text(path)

    return text
