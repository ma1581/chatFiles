
import os

from Conversion.convert import extract_text_from_pdf

def getDataByType(path):
    file = os.path.basename(path)
    if file.lower().endswith('.pdf'):
        print(file)
        print(path)
        return extract_text_from_pdf(path)
    elif file.lower().endswith('.txt'):
        return open(path,"r").read()

