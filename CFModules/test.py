'''
requirements.txt file contents:
 
langchain==0.0.154
PyPDF2==3.0.1
python-dotenv==1.0.0
streamlit==1.18.1
faiss-cpu==1.7.4
streamlit-extras
'''
 
 
import streamlit as st
from dotenv import load_dotenv
import pickle
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import os
from langchain.document_loaders import TextLoader
from langchain.embeddings import OllamaEmbeddings
from langchain.llms import Ollama
# Sidebar contents
 
def main():
    st.header("Chat with PDF 💬")
 
 
    # upload a PDF file
    pdf="ficStory.txt"
    # st.write(pdf)
    if pdf is not None:
        loader = TextLoader(pdf)

        text = open(pdf,"r").read()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
            )
        chunks = text_splitter.split_text(text=text)
 
        
        embeddings = OllamaEmbeddings(
    model="orca-mini",
    )
        VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
        with open(f"test.pkl", "wb") as f:
            pickle.dump(VectorStore, f)
 
        # embeddings = OpenAIEmbeddings()
        # VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
 
        # Accept user questions/query
        query = st.text_input("Ask questions about your PDF file:")
        # st.write(query)
 
        if query:
            docs = VectorStore.similarity_search(query=query, k=3)
 
            llm=Ollama(model="orca-mini")
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            response = chain.run(input_documents=docs, question=query)
            st.write(response)
 
if __name__ == '__main__':
    main()