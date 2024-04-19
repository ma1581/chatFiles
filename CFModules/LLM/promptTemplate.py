from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

system_prompt = """You are a helpful assistant, you will use the provided context to answer user questions.
Read the given context before answering questions and think step by step. If you can not answer a user question based on 
the provided context, inform the user. Do not use any other information for answering user. Provide a detailed answer to the question."""

system_prompt = """Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer. 
            Use three sentences maximum and keep the answer as concise as possible."""


def get_prompt_template(history=False):
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS
    if history:
        instruction = """
        Context: {history} \n {context}
        User: {question}"""
        prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
        prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
    else:
        instruction = """
        Context: {context}
        User: {question}"""
        prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
        prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)
    memory = ConversationBufferMemory(input_key="question", memory_key="history")
    return (prompt, memory,)
