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

from langchain import HuggingFaceHub






def format_docs(docs):
  formatted_docs = "\n\n".join(doc.page_content for doc in docs)  # Create the formatted string
  str1="-"*50
  print("\n")
  logging.info(str1 + "these are the documnets retrieved for this query " +str1)
  print(formatted_docs)  # Print the formatted string
  print('\n')
  return formatted_docs  # Return the formatted string for further use


embeddings=None
db=None
llm=None

def multiquery(env,query):  
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

def invoke_on_call(func,query):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        result = result.invoke(input=query)

        return result
    
    def wrapper_for_qa(*args, **kwargs):
        result = func(*args, **kwargs)
        # If the result is callable, assume it's the chain and invoke it
        if callable(result):
            result = result(query)

        return result['result']

    if(func==retrieval_qa_pipline):
        return wrapper_for_qa
    else: return wrapper


def rag(env,query):
    logging.info(f"Using RAG chain")
    retriever = db.as_retriever(search_type="similarity",search_kwargs={"k": 4})
    from langchain_core.prompts import PromptTemplate
    template = """Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use three sentences maximum and keep the answer as concise as possible.
    if any coding questions are asked , 
    answer them as best as possible eventhough they could not be related to the context.
    Please use only this format for the code   
    ``` specify coding language used \n
    write code here \n
    ``` . 

    
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
    # print(rag_chain)
    return rag_chain


def retrieval_qa_pipline(env,query):
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


def interative_main(env):

    logging.info(f"Running on: {env['processor']}")
    logging.info(f"Display Source Documents set to: {env['showSources']}")
    logging.info(f"Use history set to: {env['history']}")

    while True:
        try:
            query = input("Ask a question (or type 'quit' to exit): ")
            if query.lower() == "quit":
                break

            #uncomment the lines specific to what pipeline you want to use  

            # Retrieve and answer the question
            qa= invoke_on_call(rag,query)

            logging.info("Communicating with llm")
            answer=qa(env,query)
            logging.info("_" * 100)
            print("the answer to your question ")
            print(answer)

            # Log the interaction if logging is enabled
            if env["log"]:
                backup.log_to_csv(query, answer, env["logDirectory"])

        except KeyboardInterrupt:
            print("\n")
            time.sleep(1)
            print("\nThank You for using chatFiles")
            break

def main(env,query,file):
    #in other words singleton objs
    
    initialize_global_objects(file)

    qa= invoke_on_call(rag,query)
    answer=qa(env,query)
    return answer

def initialize_global_objects(file=None):
    global embeddings
    global db 
    global llm

    embeddings = OllamaEmbeddings(model="orca-mini", model_kwargs={"device": env["processor"]})
    db = Chroma(
            persist_directory=env["vectorDirectory"],
            embedding_function=embeddings,
            client_settings=env["CHROMA_SETTINGS"],
            collection_name=file
        )
    print(db)
    print("This is from :",db._collection)
    llm = env["model"]

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
    file="ficStory.txt"
    copy_file(env["sampleDirectory"]+file, env["digestDirectory"]+file)
    logging.info(f"Using file "+env["digestDirectory"]+file)

    # ----------------------------------------------------------------
    vectorMain(env,file)
    # newVectorMain(env,file)
    # ----------------------------------------------------------------

    initialize_global_objects(file)

    res=interative_main(env)





