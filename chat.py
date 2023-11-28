import streamlit as st
import easygui
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from Conversion.convert import extract_text_from_pdf

@st.cache(suppress_st_warning=True)
def process_file(data, user_input):
    #data = extract_text_from_pdf(uploaded_file)
    result = Ollama(model="orca-mini", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))("Context:" + data + "\nBased on only above content only, answer the below question.\n" + user_input)
    return result



import streamlit as st
# Function to process the file content

def main():
    st.title("File Upload and Processing App")

    # File Upload
    uploaded_file = st.file_uploader("Upload a text file", type=["txt","pdf"])
    # User Input
    user_input = st.text_input("Enter some text:")
    

    # Process Button
    if st.button("Process"):
        if uploaded_file is not None:
            if uploaded_file.name.lower().endswith('.pdf'):
                data=extract_text_from_pdf(uploaded_file.name)
            elif uploaded_file.name.lower().endswith('.txt'):
                data=open(uploaded_file.name,'r').read()
        if user_input:
           st.text_area("Parsed Data",data,height=250)
           output=process_file(data, user_input)
           st.text_area("BOT",output,height=500)

if __name__ == "__main__":
    main()