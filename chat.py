import streamlit as st
from orcaLang import *
# Function to process the file content
def process_file(file_content):
    # Process the file content (you can replace this with your logic)
    processed_content = file_content.decode("utf-8").split("\n")
    return processed_content
def count_words(text):
    # Split the text into words
    words = text.split()

    # Count the number of words
    num_words = len(words)

    return num_words

def main():
    st.title("File Upload and Processing App")

    # File Upload
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
    # User Input
    print("File Location: " + uploaded_file.name)

    # Process Button
    if st.button("Process"):
        if uploaded_file is not None:
            print("File Location: " + uploaded_file.name)

if __name__ == "__main__":
    main()
