from langchain.embeddings import OllamaEmbeddings
from CFModules.LLM.promptTemplate import get_prompt_template
from CFModules import backup
from CFModules.LLM.dataIngest import *
from environment import env
from langchain.chat_models import ChatOllama
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.vectorstores import Chroma

from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  # for streaming response
from langchain.callbacks.manager import CallbackManager
from langchain.chains import LLMChain
import logging
logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
import time
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

def multiquery(env,query):   
    print("Fetching embeddings...")
    embeddings = OllamaEmbeddings(model=env["model"], model_kwargs={"device": env["processor"]})
    print("Fetching db...")
    db = Chroma(
        persist_directory=env["vectorDirectory"],
        embedding_function=embeddings,
        client_settings=env["CHROMA_SETTINGS"]
    )
    print("Fetching llm")
    llm = Ollama(model=env["model"])
    print("Fetching retriever")
    retriever=MultiQueryRetriever.from_llm(retriever=db.as_retriever(),llm=llm)
    docs=retriever.get_relevant_documents(query=query)
    print(docs)
    print("Obtained docs")
    from langchain_core.prompts import PromptTemplate
    QA_PROMPT=PromptTemplate(
        input_variables=["question","context"],
        template = """Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use three sentences maximum and keep the answer as concise as possible.
    Always say "thanks for asking!" at the end of the answer.
    
    {context}
    
    Question: {question}
    
    Helpful Answer:""")
    qa_chain=LLMChain(llm=llm,prompt=QA_PROMPT)
    print("Querying....")
    out=qa_chain(inputs={
        "question":query,
        "context":"\n---\n".join([d.page_content for d in docs])
    })
    print("\n\n\n")
    print(out['text'])

def rag(env,query):
    embeddings = OllamaEmbeddings(model=env["model"], model_kwargs={"device": env["processor"]})
    db = Chroma(
        persist_directory=env["vectorDirectory"],
        embedding_function=embeddings,
        client_settings=env["CHROMA_SETTINGS"]
    )
    llm = Ollama(model=env["model"])

    retriever = db.as_retriever(search_type="similarity",search_kwargs={"k": 2})

    #retriever=db.similarity_search(query)
    retrieved_docs = retriever.get_relevant_documents(query)
    print(type(retriever))
    print(type(retrieved_docs))
    for i in retrieved_docs:
        print(type(i))
        print(i)
    #for i in range(0,len(retrieved_docs)):
    #    print(retrieved_docs[i].page_content)
    from langchain_core.prompts import PromptTemplate

    template = """Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use three sentences maximum and keep the answer as concise as possible.
    Always say "thanks for asking!" at the end of the answer.
    
    {context}
    
    Question: {question}
    
    Helpful Answer:"""
    custom_rag_prompt = PromptTemplate.from_template(template)
    rag_chain = (
        {"context": retriever| format_docs, "question": RunnablePassthrough()}
        | custom_rag_prompt
        | llm
        | StrOutputParser()
    )
    print(rag_chain)
    return rag_chain
    
def retrieval_qa_pipline(env,query):
    embeddings = OllamaEmbeddings(model=env["model"], model_kwargs={"device": env["processor"]})
    db = Chroma(
        persist_directory=env["vectorDirectory"],
        embedding_function=embeddings,
        client_settings=env["CHROMA_SETTINGS"]
    )
    llm = Ollama(model=env["model"])
    retriever = db.as_retriever()
    prompt, memory = get_prompt_template(history=env["history"])
    if env["history"]:
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
            retriever=retriever,
            return_source_documents=True,  # verbose=True,
            callbacks=callback_manager,
            chain_type_kwargs={"prompt": prompt, "memory": memory},
        )
    else:
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
            retriever=retriever,
            return_source_documents=True,  # verbose=True,
            callbacks=callback_manager,
            chain_type_kwargs={
                "prompt": prompt,
            },
        )
    return qa
'''    prompt, memory = get_prompt_template(history=env["history"])
    print(prompt)
    #llm=Ollama(model=env["model"])
    

    print(retriever)
    if env["history"]:
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
            retriever=retriever,
            return_source_documents=True,  # verbose=True,
            callbacks=callback_manager,
            chain_type_kwargs={"prompt": prompt, "memory": memory},
        )
    else:
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
            retriever=retriever,
            return_source_documents=True,  # verbose=True,
            callbacks=callback_manager,
            chain_type_kwargs={
                "prompt": prompt,
            },
        )

    return qa
'''



def main(env,query=None):
    
    logging.info(f"Running on: {env['processor']}")
    logging.info(f"Display Source Documents set to: {env['showSources']}")
    logging.info(f"Use history set to: {env['history']}")
    
    try:
        #qa = retrieval_qa_pipline(env,query)
        qa = retrieval_qa_pipline(env,query)
        logging.info("Communicating with llm")
        res = qa(query)
        answer, docs = res["result"], res["source_documents"]
        logging.info("_"*100)
        return answer
        #for chunk in qa.stream(query):
        #    print(chunk, end="", flush=True)
        # Get the answer from the chain
       
        
        # Print the result
        #print("\n\n> Question:")
        #print(query)
        #print("\n> Answer:")
        #print(answer)

        # Log the Q&A to CSV only if save_qa is True
        if env["log"]:
            backup.log_to_csv(query, answer,env["logDirectory"])
    except KeyboardInterrupt:
        print("\n")
        time.sleep(1)
        print("\nThank You for using chatFiles")
        time.sleep(1)

import shutil

def copy_file(source_path, destination_path):
    try:
        print(source_path)
        shutil.copy(source_path, destination_path)
        print(f"File copied successfully from {source_path} to {destination_path} to make VectorDB")
    except FileNotFoundError:
        print("File not found. Please check the source path.")
    except PermissionError:
        print("Permission error. Make sure you have the necessary permissions.")

if __name__ == "__main__":
    
    #This two line code exist because no upload function is added
    file="multiStory.txt"
    copy_file(env["sampleDirectory"]+file, env["digestDirectory"]+file)
    logging.info(f"Using file "+env["digestDirectory"]+file)
    #vectorMain(env,file)
    q=input("Enter a query:")
    res=main(env,q)
    print(res)





