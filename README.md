# CHAT WITH FILES


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
        -Permanent Fix:    
        ```
            sudo nano /etc/sysctl.conf
            fs.inotify.max_user_watches=524288
            sudo sysctl -p
        ```
        -Temporary Fix(Will Vanish after Restart):
        ```
            sudo sysctl fs.inotify.max_user_watches=524288
        ```
4. **Running the Project**:
   - Execute below command to run the project:
   ```
        streamlit run chat.py
   ```

