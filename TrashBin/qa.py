from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
import pickle
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.chains.question_answering import load_qa_chain


def splitter(docText):
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
            )
    return text_splitter.split_text(text=docText)
def vecstore2(docText,query):
    chunks=splitter(docText)
    embeddings = OllamaEmbeddings(
    model="orca-mini",
    )
    VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
#    with open(f"test.pkl", "wb") as f:
#        pickle.dump(VectorStore, f)
    docs = VectorStore.similarity_search(query=query, k=3)
    print("Narrowed document")
    return docs


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


def myQaChain(llm,docText,query):
    chain = load_qa_chain(llm, chain_type="map_reduce")
    print("Loaded document")
    return chain.run(input_documents=vecstore2(docText,query), question=query)