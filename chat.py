import streamlit as st
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from CFModules.Conversion.convert import *
import os
import atexit
from streamlit.logger import get_logger
from environment import env
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
    st.title("File Upload and Processing App")
    data="None"
    # File Upload
    uploaded_file = st.file_uploader("Upload a text file", type=["txt","pdf"])
    if uploaded_file: logging.info(f"File Uploaded")
    # User Input
    user_input = st.text_input("User Input:")
    if uploaded_file is not None:
        destination_path = os.path.join( env["digestDirectory"], uploaded_file.name)
        with open(destination_path, "wb") as dest_file:
            dest_file.write(uploaded_file.read())
        logging.info("File Stashed Temporarily")
        if uploaded_file.name.lower().endswith('.pdf'):
            data=extract_text_from_pdf( env["digestDirectory"]+uploaded_file.name)
            logging.info("Pdf Loaded")
        elif uploaded_file.name.lower().endswith('.txt'):
            data=open(env["digestDirectory"]+uploaded_file.name,'r').read()    
            logging.info("Text Loaded")

    # Process Button
    if st.button("Process"):
        if user_input:
           output=process_file(data, user_input)
           st.text_area("BOT",output,height=500)
    st.sidebar.text_area("Processed File Content",data,height=750)

if __name__ == "__main__":
    main()
    atexit.register(garbage_collection)

