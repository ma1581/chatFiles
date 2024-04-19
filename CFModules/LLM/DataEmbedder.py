import logging
import os

import whisper
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma


class DataEmbedder:
    def loader(self, env, filename, format):
        if format == "txt":
            loader1 = self.load_text_pdf(env["conversionType"]["txt"], env["digestDirectory"] + filename)
        elif format == "pdf":
            loader1 = self.load_text_pdf(env["conversionType"]["pdf"], env["digestDirectory"] + filename)
        elif format == "mp3":
            return self.loader(env, self.generate_text_file_version(filename), "txt")
        return loader1.load()

    def load_text_pdf(self, loader, filepath):
        return loader(filepath)

    def generate_text_file_version(self, filename):
        new_file = filename[:-4] + ".txt"
        destination_path = os.path.join(env["digestDirectory"], new_file)
        model = whisper.load_model("base")
        output = model.transcribe(env["digestDirectory"] + filename)
        data = output["text"]
        print(data)
        with open(destination_path, "w") as dest_file:
            dest_file.write(data)
        return new_file

    def vectorMain(self, env, filename, format):
        logging.info(f"Parsing Content from {env['digestDirectory']}")
        text_documents = self.loader(env, filename, format)
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
        db = Chroma.from_documents(texts, embeddings, persist_directory=env["vectorDirectory"],
                                   client_settings=env["CHROMA_SETTINGS"], collection_name=filename)
        logging.info(f"Finished Creating VDB")
