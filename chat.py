import streamlit as st
import easygui
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from Conversion.convert import extract_text_from_pdf
def process_text_input(text):
    # Replace this with your method to process the text input
    result = f"Processing: {text}"
    return result

def main():
    st.title("File Upload App")
    if st.button('Choose a file to read'):
        uploaded_file = easygui.fileopenbox(title='Add File')
    # File Upload Button

    # Check if file is uploaded
    if uploaded_file is not None:
        st.text(f"File Location: {uploaded_file}")
        # Text Input and Button
        user_input = st.text_input("Enter Text:")
        if st.button("Process"):
            llm=Ollama(model="orca-mini",callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
            result=llm("Context:"+ extract_text_from_pdf(uploaded_file)+"\nBased on only above content only, answer the below question.\n"+user_input)
            st.success(result)

if __name__ == "__main__":
    main()
