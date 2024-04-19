import logging
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

import whisper
from langchain.docstore.document import Document
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma


def loader(env, filename, format):
    if format == "txt":
        converter = env["conversionType"]["txt"]
        loader1 = converter(env["digestDirectory"] + filename)
    elif format == "pdf":
        pdfLoaderVar = env["conversionType"]["pdf"]
        loader1 = pdfLoaderVar(env["digestDirectory"] + filename)
    elif format == "mp3":
        '''
        audioLoaderVar=env["conversionType"]["mp3"]
        alv=audioLoaderVar(env["digestDirectory"]+filename)
        alv.get_segment(env["processor"]) 
        data=alv.get_text()
        '''
        new_file = filename[:-4] + ".txt"
        destination_path = os.path.join(env["digestDirectory"], new_file)

        model = whisper.load_model("base").to("cuda")
        output = model.transcribe(env["digestDirectory"] + filename)
        data = output["text"]

        print(data)
        with open(destination_path, "w") as dest_file:
            dest_file.write(data)
        return loader(env, new_file, "txt")
    return loader1.load()


def vectorMain(env, filename, format):
    logging.info(f"Parsing Content from {env['digestDirectory']}")
    text_documents = loader(env, filename, format)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    texts = text_splitter.split_documents(text_documents)

    logging.info(f"Split into {len(texts)} chunks of text")
    embeddings = OllamaEmbeddings(model="orca-mini", model_kwargs={"device": env["processor"]}, )
    logging.info(f"Pushing Embeddings into VectorBD")
    vectorstore = Chroma(persist_directory=env["vectorDirectory"], client_settings=env["CHROMA_SETTINGS"], )
    logging.info("Checking if VDB already exists")
    for i in vectorstore._client.list_collections():
        if i.name == filename:
            logging.info("VectorStore Already present")
            return
    logging.info("Creating new VDB")
    db=Chroma.from_documents(texts, embeddings, persist_directory=env["vectorDirectory"],
                          client_settings=env["CHROMA_SETTINGS"], collection_name=filename)
    logging.info(f"Finished Creating VDB")


