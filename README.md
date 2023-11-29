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
  
3. **Error Related to Streamlit** (Optional): 
   - If you get the `OSError: [Errno 28] inotify watch limit reached` error when running the project, you can run the below command to troublshoot it:
        - Permanent Fix:    
            ```
                sudo nano /etc/sysctl.conf
                fs.inotify.max_user_watches=524288
                sudo sysctl -p
            ```
        - Temporary Fix(Will Vanish after Restart):
            ```
                sudo sysctl fs.inotify.max_user_watches=524288
            ```
4. **Error Related to frontend pip library** (Optional): 
   - For the frontend library to work, a empty static folder is necessary. 
   - So run the below command if error `RunTimeError: Directory 'static/' does not exist` was found:
      ```
        mkdir static
        ```
5. **Running the Project**:
   - Execute below command to run the streamlit UI:
        ```
            streamlit run chat.py
        ```
   - Use the below syntax to execute the CLI version:
        ```
            python3 orcaLang.py --q "<question>" --f  <filename> --e <simpleModel/chatModel/vectorModel/textSplitModel>
        ``` 
       - This command uses default input:
        ```
            python3 orcaLang.py
        
            #Question : "Who are Cast of Wakanda Forever?"
            #File : wkfor.txt
            #Approach : simpleModel
        ```
        
# Bugs & Errors:
- Extent of pdf to text conversion needs to be checked
- Need to adjust the code to accept to talk freely even without input data
- videos and audio are not accepted
- Please add on more bugs if found