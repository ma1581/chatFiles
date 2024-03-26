import re
import requests
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
import streamlit as st
from langchain import HuggingFaceHub
from streamlit_option_menu import option_menu

from streamlit.logger import get_logger
from environment import env
#import faster_whisper
from faster_whisper import WhisperModel
from Vlog2 import Vlogger
import main as climain
from code_cell import main as process_code
import code_cell
# from htmlTemplates import button_template
# from htmlTemplates import script


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
def garbage_collection():
  # Perform your desired cleanup tasks here
  delete_tempFiles( env["digestDirectory"])

def main():

    # st.write(script,unsafe_allow_html=True)

    print("Calling stream main")
    if 'data' not in st.session_state:
        st.session_state.data = None
    print(st.session_state.data)
    st.title("Chat with documents using chatFiles")
    selected = option_menu(options=["Text / PDF / Audio",'Web Doc'], orientation="horizontal",menu_title=None,
         default_index=0)
    

    uploaded_file = None
    web_path=None
    web_data=None
    if selected == "Text / PDF / Audio":
        uploaded_file = st.file_uploader("Upload a text file", type=["txt","pdf","mp3"])
    # elif selected == "Video (mp4)":
    #     uploaded_file = st.file_uploader("Upload a video file", type=["mp4"])
    elif selected == "Web Doc":
        web_url=st.text_input("Enter the web url")
        if st.button("Submit"):
            if web_url:
                web_data=beautiful_soup(web_url=web_url)
                web_data=web_data.encode("utf-8")
                web_path=remove_special_characters(web_url)
                file_path = os.path.join(env["digestDirectory"] + web_path )
                with open(file_path, "wb") as file:
                    file.write(web_data)
    
    



    # uploaded_file = st.file_uploader("Upload a text file", type=["txt","pdf","mp3","mp4"])

    # Get the absolute path to the MP4 file from user input
    # file_path_input = st.text_input("Enter the absolute path to the MP4 file:")

    # Button to submit the input and process the video
    # if st.button("Submit"):
    #     if file_path_input:
    #         v=Vlogger()
    #         data=v.vid_to_text([file_path_input])
    #         print(data)
    #     else:
    #         st.warning("Please enter the absolute path to the MP4 file.")

    if uploaded_file : 
        logging.info(f"File Uploaded")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

     # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        file_name=""
        if selected=="Text / PDF / Audio":
            file_name=uploaded_file.name
        elif selected=="Web Doc":
            web_path=remove_special_characters(web_url)
            file_name=web_path
        else:
            file_name="None"

        assistant_response =climain.main(env,prompt,file_name)
        print(assistant_response)

        lang,code,description=code_cell.extract_code(assistant_response)

        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", "content": assistant_response,"new_answer":True,
            "lang":lang,"code":code,"desc":description,"output":None
            })

    # Display chat messages from history on app rerun
    for index,message in enumerate(st.session_state.messages):
        if(index==len(st.session_state.messages)-1):

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                if(message["new_answer"]==True):
                    full_response = ""
                    
                    # Simulate stream of response with milliseconds delay
                    for chunk in message["content"].split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    message["new_answer"]=False
                else:
                    message_placeholder.markdown(message["content"])

                if(message["code"] is not None):
                    message["code"]=st.text_area("code",message["code"],height=120)
                    if(st.button("run code")):
                        if(message["lang"]=="javascript"):
                            message["output"]= code_cell.run_javascript_code(message["code"])
                        elif(message["lang"]=="python"):
                            message["output"]= code_cell.run_python_code(message["code"])
                            
                if(message["code"] is not None and message["output"] is not None):
                    st.text_area("Output",message["output"])
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # File Upload
    if uploaded_file is not None and (st.session_state.data==None or uploaded_file.name!=st.session_state.data) and selected=="Text / PDF / Audio":
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

    elif web_path is not None and selected=="Web Doc" and (st.session_state.data==None or web_path!=st.session_state.data):
        vectorMain(env,web_path,"txt")
        st.session_state.data=web_path
        logging.info("Text Loaded into Vector DB")



    with st.sidebar:
        option = st.selectbox(
           "Select Model",
           ("Ollama:Orca-mini", "HF:Mistral"),
           index=None,
           placeholder="....",
        )
        if option == "Ollama:Orca-mini":
            env["model"]=Ollama(model="orca-mini")
        elif option == "HF:Mistral" :
            env["model"]=HuggingFaceHub(repo_id="mistralai/Mistral-7B-v0.1",huggingfacehub_api_token="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")
        else:
            env["model"]=None
        st.write('You selected:', option)

from bs4 import BeautifulSoup

def remove_special_characters(input_string):
    # Define a regular expression pattern to match special characters
    pattern = r'[^a-zA-Z0-9\s]'  # Matches any character that is not alphanumeric or whitespace
    
    # Use the sub() function from the re module to replace matched characters with an empty string
    return re.sub(pattern, '', input_string)

def beautiful_soup(web_url):
    try:
        # Send a GET request to the URL
        response = requests.get(web_url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the text content from the parsed HTML
            text_content = soup.get_text()
            # print("the text coontent from the web ul is " + text_content)
            
            return text_content
        else:
            print(f"Failed to retrieve content. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

        
if __name__ == "__main__":
    main()
    atexit.register(garbage_collection)
