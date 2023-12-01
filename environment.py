import os
from CFModules.Conversion.textFileLoader import txtToString
from CFModules.Conversion.convert import extract_text_from_pdf
env={
    "model":"orca-mini",
    "rootDirectory":os.path.dirname(os.path.realpath(__file__)),
    "digestDirectory": os.path.dirname(os.path.realpath(__file__))+"/Data/TempFiles/",
    "conversionType":{
        "txt":txtToString,
        "pdf":extract_text_from_pdf
    }
}