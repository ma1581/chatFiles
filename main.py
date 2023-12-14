from langchain.embeddings import OllamaEmbeddings
from CFModules.LLM.promptTemplate import get_prompt_template
from CFModules import backup
from CFModules.LLM.dataIngest import *
from environment import env
from langchain.chat_models import ChatOllama

# from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  # for streaming response
from langchain.callbacks.manager import CallbackManager

import logging
import time

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


def retrieval_qa_pipline(env):
    embeddings = OllamaEmbeddings(model=env["model"], model_kwargs={"device": env["processor"]})
    db = Chroma(
        persist_directory=env["vectorDirectory"],
        embedding_function=embeddings,
        client_settings=env["CHROMA_SETTINGS"]
    )
    retriever = db.as_retriever()
    prompt, memory = get_prompt_template(history=env["history"])

    #llm=Ollama(model=env["model"])
    llm = ChatOllama(model=env["model"])


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

def conversational_qa(vectorstore):
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationalRetrievalChain

    llm = ChatOllama(model=env["model"])
    embeddings = OllamaEmbeddings(model=env["model"], model_kwargs={"device": env["processor"]})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        chain_type="map_reduce"
    )
    return conversation_chain
    
    




def main(env,vectorstore):
    
    logging.info(f"Running on: {env['processor']}")
    logging.info(f"Display Source Documents set to: {env['showSources']}")
    logging.info(f"Use history set to: {env['history']}")

    # check if models directory do not exist, create a new one and store models here.
    '''
    MODELS_PATH="./models"
    if not os.path.exists(MODELS_PATH):
        os.mkdir(MODELS_PATH)
    '''

    # qa = retrieval_qa_pipline(env)
    qa=conversational_qa(vectorstore)


    # Interactive questions and answers
    while True:
        try:
            query = input("\nEnter a query: ")
            if query == "exit":
                break
            # Get the answer from the chain
            res = qa(query)


            for i, message in enumerate(res['chat_history']):
                if i % 2 == 0:
                    print('user question' +str(i) +": " + message.content)
                else:
                    print('bot answer ' +str(i) +": " + message.content)
                print('\n')
                    
        except KeyboardInterrupt:
            print("\n")
            time.sleep(1)
            print("\nThank You for using chatFiles")
            time.sleep(1)
            break

import shutil

def copy_file(source_path, destination_path):
    try:
        shutil.copy(source_path, destination_path)
        print(f"File copied successfully from {source_path} to {destination_path} to make VectorDB")
    except FileNotFoundError:
        print("File not found. Please check the source path.")
    except PermissionError:
        print("Permission error. Make sure you have the necessary permissions.")

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )

    #This two line code exist because no upload function is added
    file="ficStory.txt"
    copy_file(env["sampleDirectory"]+file, env["digestDirectory"]+file)
    
    # vectorMain(env)
    from CFModules.LLM.dataIngest import vectorMainWithFaiss
    vectorstore=vectorMainWithFaiss(env)
    main(env,vectorstore)







