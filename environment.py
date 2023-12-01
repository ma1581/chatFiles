import os
from CFModules.Conversion.textFileLoader import txtToString
from CFModules.Conversion.convert import extract_text_from_pdf
from langchain.document_loaders import PDFMinerLoader, TextLoader
from chromadb.config import Settings

env={
    "model":"orca-mini",
    "rootDirectory":os.path.dirname(os.path.realpath(__file__)),
    "digestDirectory": os.path.dirname(os.path.realpath(__file__))+"/Data/TempFiles/",
    "sampleDirectory": os.path.dirname(os.path.realpath(__file__))+"/Data/SampleFiles/",
    "vectorDirectory": os.path.dirname(os.path.realpath(__file__))+"/Data/VectorDB/",
    "CHROMA_SETTINGS" : Settings(anonymized_telemetry=False,is_persistent=True),
    "conversionType":{
        "txt":TextLoader,
        "pdf":PDFMinerLoader
    },
    "cpuCount":os.cpu_count()
}
 