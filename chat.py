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
            # Read the file content
            file_content = uploaded_file.read()
            # Process the file content
 
            # Display the processed content
        else:
            file_content=b'Nothing'
        
        if user_input:
           output=query(file_content.decode('utf-8'),user_input)
           num_of_words=count_words(output)
           lines=output.count("\n")
            # Process the user input (you can replace this with your logic)
           st.text_area("Processed User Input", output, height=int(25 *((num_of_words/20)+lines)))
    st.sidebar.text_area("Processed User Input",file_content.decode('utf-8'))        

if __name__ == "__main__":
    main()
