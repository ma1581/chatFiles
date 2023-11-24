from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts import ChatPromptTemplate

from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.prompts import HumanMessagePromptTemplate
from langchain.schema.messages import SystemMessage
from langchain.chat_models import ChatOllama
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
def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--q",type=str,help="This is the Query",default="How did Tollar Hugen's true identity and role as a guardian of realms unfold during his journey with Elara, and what impact did it have on the town of Eldoria?")
    parser.add_argument("--f",type=str,help="This is File Location",default="ficStory.txt")
    parser.add_argument("--e",type=str,help="Emphasis")
    args=parser.parse_args()
    if args.e=='chatModel':
        print("chatModel Answer")
        llm,vector=setupModelAndData(args.f)
        vectorstore=vector
        chat_model = ChatOllama(model="orca-mini",verbose=True,callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),)
        template = """[INST] <<SYS>> Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer. 
            Use three sentences maximum and keep the answer as concise as possible. <</SYS>>
            {context}
            Question: {question}
            Helpful Answer:[/INST]"""
        QA_CHAIN_PROMPT = PromptTemplate(
            input_variables=["context", "question"],
            template=template,
        )

        qa_chain = RetrievalQA.from_chain_type(
            chat_model,
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
        )

        result = qa_chain({"query": args.q})
    elif args.e=='vectorModel':
        print("vectorModel Answer")
        llm,vector=setupModelAndData(args.f)
        Query(llm,vector,args.q)
    elif args.e=='textSplitModel':
        ouput=DocSpecifc(args.q,args.f)
        print(ouput)
    else:
        print("Simple Answer")
        llm=Ollama(model="orca-mini",callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
        print(llm("Context:"+open(args.f,"r").read()+"\nBased on only above content only, answer the below question.\n"+args.q))


def setupModelAndData(file):
    llm=Ollama(model="orca-mini",callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))


    loader = TextLoader(file)

    data = loader.load()


    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=0)
    all_splits=text_splitter.split_documents(data)

    vectorstore=Chroma.from_documents(documents=all_splits,embedding=OllamaEmbeddings(
    model="orca-mini",
    ))
    return llm,vectorstore

def Query(llm,vectorstore,question):
    qachain=RetrievalQA.from_chain_type(llm,retriever=vectorstore.as_retriever())
    return qachain({"query":question})
def splitter(pdf):
    text = open(pdf,"r").read()
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
            )
    return text_splitter.split_text(text=text)
def vecstore2(query,file):
    chunks=splitter(file)
    embeddings = OllamaEmbeddings(
    model="orca-mini",
    )
    VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
    with open(f"test.pkl", "wb") as f:
        pickle.dump(VectorStore, f)
    docs = VectorStore.similarity_search(query=query, k=3)
    return docs
def DocSpecifc(question,file):
    llm=Ollama(model="orca-mini")
    chain = load_qa_chain(llm=llm, chain_type="stuff")
    return chain.run(input_documents=vecstore2(question,file), question=question)

if __name__=="__main__":
    main()