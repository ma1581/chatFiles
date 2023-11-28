# CHAT WITH FILES
This is still in development and has certain parts which is not detailed in the Readme File.
 
`Note: The Known Bugs in the system are listed below`
# Configuration & Usage:

Before you can use this project, you need remember this repository and configuration is strictly only for Linux System. Follow these steps to get started:
1. **Ollama & Orca-mini Setup**:
   - Run the Below Command to Install Ollama in you local System
     ```
     curl https://ollama.ai/install.sh | sh
     ```

   - Once Ollama is installed ,run the below command:
     ```
     ollama run orca-mini
     ```
    - The above command pulls orca-mini & you can use it to check the performance of the LLM
    
2. **Installing required PIP packages**:
   - Run the below Command to install the required PIP packages:
     ```
        pip install -r requirements.txt
     ```

4. **Running the Project**:
   - Execute below command to run the project:
        ```
            python3 orcaLang.py
        ```
        - This command uses default input as below:
            - Question : "Who are Cast of Wakanda Forever?"
            - File : wkfor.txt
            - Approach : simpleModel
   -Below is the template to use custom inputs:
        ```
            python3 orcaLang.py --q "<question>" --f  <filename> --e <simpleModel/chatModel/vectorModel/textSplitModel>
        ``` 

# Configuration & Usage:
- st.cache is deprecated
- Extent of pdf to text conversion needs to be checked
- Need to adjust the code to accept to talk freely even without input data
- Only the files in the source is accepted
- Only pdf and text files are accepted
- Need to update the way document is loaded , so that files from anywhere can be loaded(internet/local).Currently restricted to code source directory.
- Please add on more bugs if found