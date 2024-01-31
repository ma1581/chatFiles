__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import os
from CFModules.Conversion.textFileLoader import txtToString
from CFModules.Conversion.convert import extract_text_from_pdf
from langchain.document_loaders import PDFMinerLoader, TextLoader
from CFModules.Conversion.audioLoader import AudioLoader
from chromadb.config import Settings

#import torch
#pro="cuda" if torch.cuda.is_available() else "cpu"
#del sys.modules['torch']

env={
    "model":None,
    "rootDirectory":os.path.dirname(os.path.realpath(__file__)),
    "digestDirectory": os.path.dirname(os.path.realpath(__file__))+"/Data/TempFiles/",
    "sampleDirectory": os.path.dirname(os.path.realpath(__file__))+"/Data/SampleFiles/",
    "vectorDirectory": os.path.dirname(os.path.realpath(__file__))+"/Data/VectorDB/",
    "logDirectory": os.path.dirname(os.path.realpath(__file__))+"/Data/Log",
    "uploadedVidsDirectory":os.path.dirname(os.path.realpath(__file__))+'/Data/UploadedVids/',
    "tempFramesDirectory":os.path.dirname(os.path.realpath(__file__))+'/Data/TempFrames/',
    "frameSamplingRate":3,
    "CHROMA_SETTINGS" : Settings(anonymized_telemetry=False,is_persistent=True),
    "conversionType":{
        "txt":TextLoader,
        "pdf":PDFMinerLoader,
        "mp3":AudioLoader
    },
    "cpuCount":os.cpu_count(),
    "processor":"cuda",
    "showSources":True,
    "history":False,
    "log":True
}
 