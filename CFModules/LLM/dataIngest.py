import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import logging
import click
import torch
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings


def split_documents(documents: list[Document]) -> tuple[list[Document], list[Document]]:
    # Splits documents for correct Text Splitter
    text_docs, python_docs = [], []
    for doc in documents:
        if doc is not None:
           file_extension = os.path.splitext(doc.metadata["source"])[1]
           if file_extension == ".py":
               python_docs.append(doc)
           else:
               text_docs.append(doc)
    return text_docs, python_docs

def load_single_document(file_path,env):
    # Loads a single document from a file path
    try:
       file_extension = os.path.splitext(file_path)[1][1:]
       loader_class = env["conversionType"].get(file_extension)
       if loader_class:
           file_log(file_path + ' loaded.',env)
           loader = loader_class(file_path)
       else:
           file_log(file_path + ' document type is undefined.',env)
           raise ValueError("Document type is undefined")
       return loader.load()[0]
    except Exception as ex:
       file_log('%s loading error: \n%s' % (file_path, ex),env)
       return None 

def loadDocument(env):
    files=[]
    print(env["digestDirectory"])
    for loc, dir, file in os.walk(env["digestDirectory"]):
        for file_name in file:
            file_extension = os.path.splitext(file_name)[1]
            source_file_path = os.path.join(loc, file_name)
            if file_extension[1:] in env["conversionType"].keys():
                files.append(os.path.join(loc, file_name))
    print(files)
    n_workers = min(env["cpuCount"], max(len(files), 1))
    chunksize = round(len(files) / n_workers)
    docs = []
    with ProcessPoolExecutor(n_workers) as executor:
        futures = []
        # split the load operations into chunks
        for i in range(0, len(files), chunksize):
            # select a chunk of filenames
            filepaths = files[i : (i + chunksize)]
            # submit the task
            try:
               future = executor.submit(load_document_batch, filepaths,env)
            except Exception as ex:
               file_log('executor task failed: %s' % (ex),env)
               future = None
            if future is not None:
               futures.append(future)
        # process all results
        for future in as_completed(futures):
            # open the file and load the data
            try:
                contents, _ = future.result()
                docs.extend(contents)
            except Exception as ex:
                file_log('Exception: %s' % (ex),env)
    print(docs)         
    return docs

def file_log(logentry,env):
   file1 = open(env["logDirectory"]+"/file_ingest.log","a")
   file1.write(logentry + "\n")
   file1.close()
   print(logentry + "\n")

def load_document_batch(filepaths,env):
    logging.info("Loading document batch")
    # create a thread pool
    with ThreadPoolExecutor(len(filepaths)) as exe:
        # load files
        futures = [exe.submit(load_single_document, name,env) for name in filepaths]
        # collect data
        if futures is None:
           file_log( 'Something failed to submit',env)
           return None
        else:
           data_list = [future.result() for future in futures]
           # return data and file paths
           return (data_list, filepaths)


def vectorMain(env):
    # Load documents and split in chunks
    logging.info(f"Loading documents from {env['digestDirectory']}")
    documents = loadDocument(env)
    logging.info(f"Finished loading documents")
    text_documents, python_documents = split_documents(documents)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=880, chunk_overlap=200
    )
    texts = text_splitter.split_documents(text_documents)
    texts.extend(python_splitter.split_documents(python_documents))
    logging.info(f"Loaded {len(documents)} documents from {env['digestDirectory']}")
    logging.info(f"Split into {len(texts)} chunks of text")

    # Create embeddings
    embeddings = OllamaEmbeddings(
        model=env["model"],
        model_kwargs={"device": "cuda"},
    )
    # change the embedding type here if you are running into issues.
    # These are much smaller embeddings and will work for most appications
    # If you use HuggingFaceEmbeddings, make sure to also use the same in the
    # run_localGPT.py file.

    # embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    db = Chroma.from_documents(
        texts,
        embeddings,persist_directory=env["vectorDirectory"],
        client_settings=env["CHROMA_SETTINGS"]
    )


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    vectorMain()