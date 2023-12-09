__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    

import streamlit as st
from dotenv import load_dotenv
from htmlTemplates import css, bot_template, user_template
from main import retrieval_qa_pipline
from environment import env
from CFModules.LLM.dataIngest import vectorMain




def handle_userinput(user_question):
    response = st.session_state.conversation(user_question)
    st.session_state.chat_history.append([user_question,response['result']])

    
        
            
def place_uploaded_docs(uploaded_files):
    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            file_path = env['digestDirectory']+uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            st.success(f"Document '{uploaded_file.name}' has been saved successfully!")



def main():
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)
    
    # print the messages 
    # for i, message in enumerate(st.session_state.chat_history):
    #     st.write(user_template.replace(
    #         "{{MSG}}", message[0]), unsafe_allow_html=True)
    #     st.write(bot_template.replace(
    #         "{{MSG}}", message[1]), unsafe_allow_html=True)
    for i, message in reversed(list(enumerate(st.session_state.chat_history))):
        st.write(bot_template.replace("{{MSG}}", message[1]), unsafe_allow_html=True)
        st.write(user_template.replace("{{MSG}}", message[0]), unsafe_allow_html=True)


    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):

                #process uploadede docs
                #vids should be converted to text and place in digest dir as place_uploaded_docs is doing
                place_uploaded_docs(pdf_docs)
                vectorMain(env)
                

                # create conversation chain
                st.session_state.conversation =retrieval_qa_pipline(env)
                print("\nthe converstaion obj is :")
                print(st.session_state.conversation)





import os
import atexit

def garbage_collection():
  # Perform your desired cleanup tasks here
  delete_tempFiles("./Data/TempFiles/")

def delete_tempFiles(directory_path):
    try:
        # Get the list of all files in the directory
        files = os.listdir(directory_path)
        print(files)

        # Iterate over each file and delete
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Error deleting files: {e}")



if __name__ == '__main__':
    main()
    atexit.register(garbage_collection)
