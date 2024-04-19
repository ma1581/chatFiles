import atexit
import os
import re
import time

import requests
import streamlit as st
from bs4 import BeautifulSoup
from langchain.llms import HuggingFaceHub
from langchain.llms import Ollama
from streamlit.logger import get_logger
from streamlit_option_menu import option_menu

import code_cell
import main as climain
from CFModules.LLM.DataEmbedder import DataEmbedder
from environment import env

logging = get_logger(__name__)


def delete_tempFiles(directory_path):
    try:
        files = os.listdir(directory_path)
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.info("Deleted File " + file_name)
    except Exception as e:
        logging.info(f"Error deleting files: {e}")


@st.cache_data()
def garbage_collection():
    delete_tempFiles(env["digestDirectory"])


def main():
    logging.info(f"The app is Running......")
    if "data" not in st.session_state:
        st.session_state.data = None
    st.title("Chat with documents using chatFiles")
    selected = option_menu(options=["Text / PDF / Audio", "Web Doc"], orientation="horizontal", menu_title=None,
                           default_index=0, )

    uploaded_file = None
    web_path = None
    if selected == "Text / PDF / Audio":
        uploaded_file = st.file_uploader("Upload a text file", type=["txt", "pdf", "mp3"])
    elif selected == "Web Doc":
        web_url = st.text_input("Enter the web url")
        if st.button("Submit"):
            logging.info(f"Initiating Web Data Parsing")
            if web_url:
                web_data = beautiful_soup(web_url=web_url)
                web_data = web_data.encode("utf-8")
                web_path = remove_special_characters(web_url)
                file_path = os.path.join(env["digestDirectory"] + web_path)
                with open(file_path, "wb") as file:
                    file.write(web_data)

    if uploaded_file:
        logging.info(f"File Uploaded")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        if selected == "Text / PDF / Audio":
            file_name = uploaded_file.name
        elif selected == "Web Doc":
            web_path = remove_special_characters(web_url)
            file_name = web_path
        else:
            file_name = "None"
        assistant_response = climain.main(env, prompt, file_name)
        logging.info("Response from LLM ===> {assistant_response}")
        lang, code, description = code_cell.extract_code(assistant_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response, "new_answer": True, "lang": lang, "code": code,
             "desc": description, "output": None, })
    for index, message in enumerate(st.session_state.messages):
        if index == len(st.session_state.messages) - 1:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                if message["new_answer"] == True:
                    full_response = ""

                    for chunk in message["content"].split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    message["new_answer"] = False
                else:
                    message_placeholder.markdown(message["content"])

                if message["code"] is not None:
                    message["code"] = st.text_area("code", message["code"], height=120)
                    if st.button("run code"):
                        if message["lang"] == "javascript":
                            message["output"] = code_cell.run_javascript_code(message["code"])
                        elif message["lang"] == "python":
                            message["output"] = code_cell.run_python_code(message["code"])

                if message["code"] is not None and message["output"] is not None:
                    st.text_area("Output", message["output"])
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    embedded = DataEmbedder()
    if (uploaded_file is not None and (
            st.session_state.data == None or uploaded_file.name != st.session_state.data) and selected == "Text / PDF / Audio"):
        logging.info(f"Detected File type: {uploaded_file.type}")
        logging.info(f"Duplicating file")
        destination_path = os.path.join(env["digestDirectory"], uploaded_file.name)
        with open(destination_path, "wb") as dest_file:
            dest_file.write(uploaded_file.read())
        logging.info("File Stashed Temporarily")
        logging.info(f"Extacting Content")
        if uploaded_file.name.lower().endswith(".pdf"):
            embedded.vectorMain(env, uploaded_file.name, "pdf")
            st.session_state.data = uploaded_file.name
            logging.info("Pdf Loaded into Vector DB")
        elif uploaded_file.name.lower().endswith(".txt"):
            embedded.vectorMain(env, uploaded_file.name, "txt")
            st.session_state.data = uploaded_file.name
            logging.info("Text Loaded into Vector DB")
        elif uploaded_file.name.lower().endswith(".mp3"):
            embedded.vectorMain(env, uploaded_file.name, "mp3")
            st.session_state.data = uploaded_file.name
            logging.info("MP3 Loaded into Vector DB")

    elif (web_path is not None and selected == "Web Doc" and (
            st.session_state.data == None or web_path != st.session_state.data)):
        embedded.vectorMain(env, web_path, "txt")
        st.session_state.data = web_path
        logging.info("Text Loaded into Vector DB")

    with st.sidebar:
        option = st.selectbox("Select Model", ("Ollama:Orca-mini", "HF:Mistral"), index=None, placeholder="....", )
        if option == "Ollama:Orca-mini":
            logging.info("Using Orca-mini")
            env["model"] = Ollama(model="orca-mini")
        elif option == "HF:Mistral":
            logging.info("Using Mistral")
            env["model"] = HuggingFaceHub(repo_id="mistralai/Mistral-7B-v0.1",
                                          huggingfacehub_api_token="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")
        else:
            env["model"] = None
        st.write("You selected:", option)


def remove_special_characters(input_string):
    pattern = r"[^a-zA-Z0-9\s]"
    return re.sub(pattern, "", input_string)


def beautiful_soup(web_url):
    try:
        response = requests.get(web_url)
        if response.status_code == 200:
            logging.info(f"Response Successful from URL")
            soup = BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text()
            text_content = remove_consecutive_newlines(text_content)
            logging.info(f"Parsing completed")
            return text_content
        else:
            logging.warning(f"Failed to retrieve content. Status code: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None


def remove_consecutive_newlines(text):
    pattern = r"\n+"
    cleaned_text = re.sub(pattern, "\n", text)
    return cleaned_text.strip()


if __name__ == "__main__":
    main()
    atexit.register(garbage_collection)
