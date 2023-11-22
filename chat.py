import streamlit as st
from orcaQuery import query
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
    user_input = st.text_input("Enter some text:")
    

    # Process Button
    if st.button("Process"):
        if uploaded_file is not None:
            file_content = uploaded_file.read()
            file_content=file_content.decode('utf-8')
            que=file_content+"\n\nAbove is the content extracted from a File.Answer the below Question based on the above Content alone.\n"+user_input+"\n\nPS:If the information relating a question is not available in the Content, simply say \"This Question is not within the Context of the Provided File\""
        else:
            que=user_input
        
        if user_input:
           print(query)
           output=query(que)
           num_of_words=count_words(output)
           lines=output.count("\n")
            # Process the user input (you can replace this with your logic)
           st.text_area("Processed User Input", output, height=int(25 *((num_of_words/20)+lines)))
    st.sidebar.text_area("Processed User Input",file_content)        

if __name__ == "__main__":
    main()
