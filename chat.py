import streamlit as st
import random
import time
import streamlit as st
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from CFModules.Conversion.convert import *
from CFModules.LLM.dataIngest import * 
import os
#import torch
import atexit
from streamlit.logger import get_logger
from environment import env
#import faster_whisper
from faster_whisper import WhisperModel
from Vlog2 import Vlogger
import main as climain
#from CFModules.Conversion.audioLoader import audio_to_text_model
logging = get_logger(__name__)
def delete_tempFiles(directory_path):
    try:
        # Get the list of all files in the directory
        files = os.listdir(directory_path)
        
        # Iterate over each file and delete
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.info("Deleted File "+file_name)
    except Exception as e:
        logging.info(f"Error deleting files: {e}")
@st.cache_data()
def process_file(data, user_input):
    #data = extract_text_from_pdf(uploaded_file)
    result = Ollama(model="orca-mini", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))("Context:" + data + "\nBased on only above content only, answer the below question.\n" + user_input)
    return result
def garbage_collection():
  # Perform your desired cleanup tasks here
  delete_tempFiles( env["digestDirectory"])

def main():
    print("Calling stream main")
    if 'data' not in st.session_state:
        st.session_state.data = None
    print(st.session_state.data)
    st.title("Chat with documents using chatFiles")
    uploaded_file = st.file_uploader("Upload a text file", type=["txt","pdf","mp3","mp4"])
    # Get the absolute path to the MP4 file from user input
    # file_path_input = st.text_input("Enter the absolute path to the MP4 file:")

    # Button to submit the input and process the video
    # if st.button("Submit"):
    #     if file_path_input:
    #         v=Vlogger()
    #         data=v.vid_to_text([file_path_input])
    #     else:
    #         st.warning("Please enter the absolute path to the MP4 file.")
    if uploaded_file : 
        logging.info(f"File Uploaded")
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # File Upload
    if uploaded_file is not None and (st.session_state.data==None or uploaded_file.name!=st.session_state.data):
        logging.info(f"Duplicating file")
        destination_path = os.path.join( env["digestDirectory"], uploaded_file.name)
        with open(destination_path, "wb") as dest_file:
            dest_file.write(uploaded_file.read())
        logging.info("File Stashed Temporarily")
        logging.info(f"Extacting Content")
        if uploaded_file.name.lower().endswith('.pdf'):
            vectorMain(env,uploaded_file.name,"pdf")
            st.session_state.data=uploaded_file.name
            logging.info("Pdf Loaded")
        elif uploaded_file.name.lower().endswith('.txt'):
            vectorMain(env,uploaded_file.name,"txt")
            st.session_state.data=uploaded_file.name
            logging.info("Text Loaded into Vector DB")
        elif uploaded_file.name.lower().endswith('.mp3'):        
            vectorMain(env,uploaded_file.name,"mp3")            
            st.session_state.data=uploaded_file.name
            logging.info("MP3 Loaded")
        

    

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            #assistant_response = process_file(data, prompt)
            assistant_response =climain.main(env,prompt,uploaded_file.name)
            # Simulate stream of response with milliseconds delay
            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})


    st.sidebar.text_area("Processed File Content",st.session_state.data if "data" in st.session_state else "None",height=750)

if __name__ == "__main__":
    main()
    atexit.register(garbage_collection)
