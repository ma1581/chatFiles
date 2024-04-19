from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from CFModules.LLM.dataIngest import *
from CFModules.LLM.promptTemplate import get_prompt_template
from environment import env

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
embeddings = None
db = None
llm = None


def format_docs(docs):
    formatted_docs = "\n\n".join(doc.page_content for doc in docs)
    str1 = "-" * 50
    print("\n")
    logging.info(str1 + "these are the documnets retrieved for this query " + str1)
    print(formatted_docs)
    print('\n')
    return formatted_docs


def invoke_on_call(func, query):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        result = result.invoke(input=query)

        return result

    def wrapper_for_qa(*args, **kwargs):
        result = func(*args, **kwargs)
        if callable(result):
            result = result(query)

        return result['result']

    if (func == retrieval_qa_pipline):
        return wrapper_for_qa
    else:
        return wrapper


def rag(env, query):
    logging.info(f"Using RAG chain")
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})
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
    rag_chain = ({"context": retriever | format_docs,
                  "question": RunnablePassthrough()} | custom_rag_prompt | llm | StrOutputParser())
    return rag_chain


def retrieval_qa_pipline(env, query):
    retriever = db.as_retriever()
    prompt, memory = get_prompt_template(history=env["history"])
    if env["history"]:
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff",
                                         # try other chains types as well. refine, map_reduce, map_rerank
                                         retriever=retriever, return_source_documents=True,  # verbose=True,
                                         callbacks=callback_manager,
                                         chain_type_kwargs={"prompt": prompt, "memory": memory}, )
    else:
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff",
                                         # try other chains types as well. refine, map_reduce, map_rerank
                                         retriever=retriever, return_source_documents=True,  # verbose=True,
                                         callbacks=callback_manager, chain_type_kwargs={"prompt": prompt, }, )
    return qa


def main(env, query, file):
    # in other words singleton objs

    initialize_global_objects(file)

    qa = invoke_on_call(rag, query)
    answer = qa(env, query)
    return answer


def initialize_global_objects(file="None"):
    global embeddings
    global db
    global llm

    embeddings = OllamaEmbeddings(model="orca-mini", model_kwargs={"device": env["processor"]})
    db = Chroma(persist_directory=env["vectorDirectory"], embedding_function=embeddings,
                client_settings=env["CHROMA_SETTINGS"], collection_name=file)
    print(db)
    print("This is from :", db._collection)
    llm = env["model"]
