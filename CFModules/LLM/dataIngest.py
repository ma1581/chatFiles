import logging
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

import whisper
from langchain.docstore.document import Document
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma


def split_documents(documents: list[Document]) -> tuple[list[Document], list[Document]]:
    text_docs, python_docs = [], []
    for doc in documents:
        if doc is not None:
            file_extension = os.path.splitext(doc.metadata["source"])[1]
            if file_extension == ".py":
                python_docs.append(doc)
            else:
                text_docs.append(doc)
    return text_docs, python_docs


def load_single_document(file_path, env):
    try:
        file_extension = os.path.splitext(file_path)[1][1:]
        loader_class = env["conversionType"].get(file_extension)
        if loader_class:
            file_log(file_path + ' loaded.', env)
            loader = loader_class(file_path)
        else:
            file_log(file_path + ' document type is undefined.', env)
            raise ValueError("Document type is undefined")
        return loader.load()[0]
    except Exception as ex:
        file_log('%s loading error: \n%s' % (file_path, ex), env)
        return None


def loadDocument(env):
    files = []
    print(env["digestDirectory"])
    for loc, dir, file in os.walk(env["digestDirectory"]):
        for file_name in file:
            file_extension = os.path.splitext(file_name)[1]
            if file_extension[1:] in env["conversionType"].keys():
                files.append(os.path.join(loc, file_name))
    print(files)
    n_workers = min(env["cpuCount"], max(len(files), 1))
    chunksize = round(len(files) / n_workers)
    docs = []
    with ProcessPoolExecutor(n_workers) as executor:
        futures = []
        for i in range(0, len(files), chunksize):
            filepaths = files[i: (i + chunksize)]
            try:
                future = executor.submit(load_document_batch, filepaths, env)
            except Exception as ex:
                file_log('executor task failed: %s' % (ex), env)
                future = None
            if future is not None:
                futures.append(future)
        for future in as_completed(futures):
            try:
                contents, _ = future.result()
                docs.extend(contents)
            except Exception as ex:
                file_log('Exception: %s' % (ex), env)
    print(docs)
    return docs


def file_log(logentry, env):
    file1 = open(env["logDirectory"] + "/file_ingest.log", "a")
    file1.write(logentry + "\n")
    file1.close()
    print(logentry + "\n")


def load_document_batch(filepaths, env):
    logging.info("Loading document batch")
    # create a thread pool
    with ThreadPoolExecutor(len(filepaths)) as exe:
        # load files
        futures = [exe.submit(load_single_document, name, env) for name in filepaths]
        # collect data
        if futures is None:
            file_log('Something failed to submit', env)
            return None
        else:
            data_list = [future.result() for future in futures]
            # return data and file paths
            return (data_list, filepaths)


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
        newfile = filename[:-4] + ".txt"
        destination_path = os.path.join(env["digestDirectory"], newfile)

        model = whisper.load_model("base").to("cuda")
        output = model.transcribe(env["digestDirectory"] + filename)
        data = output["text"]

        print(data)
        with open(destination_path, "w") as dest_file:
            dest_file.write(data)
        return loader(env, newfile, "txt")
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

    Chroma.from_documents(texts, embeddings, persist_directory=env["vectorDirectory"],
                          client_settings=env["CHROMA_SETTINGS"], collection_name=filename)
    logging.info(f"Finished Creating VDB")


def vectorMainWithFaiss(env):
    from langchain.vectorstores import FAISS

    logging.info(f"Loading documents from {env['digestDirectory']}")
    documents = loadDocument(env)
    logging.info(f"Finished loading documents")
    text_documents, python_documents = split_documents(documents)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = ""
    for doc in text_documents:
        texts += doc.page_content

    for doc in python_documents:
        texts += doc.page_content

    texts = text_splitter.split_text(texts)

    print(f"Loaded {len(documents)} documents from {env['digestDirectory']}")
    print(f"Split into {len(texts)} chunks of text")

    embeddings = OllamaEmbeddings(model=env["model"], model_kwargs={"device": env["processor"]}, )
    vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings)
    return vectorstore
