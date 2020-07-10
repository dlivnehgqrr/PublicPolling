from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO

def pdf_to_text(path, num_pages_to_skip):
    manager = PDFResourceManager()
    retstr = BytesIO()
    layout = LAParams(all_texts=True)
    device = TextConverter(manager, retstr, laparams=layout)
    filepath = open(path, 'rb')
    interpreter = PDFPageInterpreter(manager, device)
    count = 0
    for page in PDFPage.get_pages(filepath, check_extractable=True):
        count = count + 1
        if count <= num_pages_to_skip:
            continue
        interpreter.process_page(page)
        text = retstr.getvalue()
    filepath.close()
    device.close()
    retstr.close()
    return text