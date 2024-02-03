import streamlit as st
import subprocess

def run_python_code(input_code):
    try:
        # Create subprocess
        process = subprocess.Popen(['python', '-c', input_code],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)

        # Capture output and errors
        output, error = process.communicate()

        # Check if the subprocess was successful
        if process.returncode == 0:
            return f"{output}"
        else:
            return f"Error:\n{error}"
    except Exception as e:
        return f"An error occurred: {e}"
    

def run_javascript_code(input_code):
    try:
        # Create subprocess
        process = subprocess.Popen(['nodejs', '-e', input_code],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)

        # Capture output and errors
        output, error = process.communicate()

        # Check if the subprocess was successful
        if process.returncode == 0:
            return f"{output}"
        else:
            return f"Error:\n{error}"
    except Exception as e:
        return f"An error occurred: {e}"

def main(llm_output):
    lang,code,description=extract_code(llm_output)

    if(lang!="false"):
        # Input box for Python code
        python_code = st.text_area("Enter javascript Code:", code, height=100)

        if st.button("Run Code"):
            if(lang=='javascript'):
                # Display Python output
                output = run_javascript_code(code)
                st.text_area("Python Output:", output, height=100)
            elif(lang=="python "):
                # Display Python output
                output = run_python_code(code)
                st.text_area("Python Output:", output, height=100)
        return description
    else:
        return description



import re




def extract_code(llm_output):
    match_p = re.search(r'```\s*python\n(.*?)\n```', llm_output, re.DOTALL)
    match_j=re.search(r'```\s*javascript\n(.*?)\n```', llm_output, re.DOTALL)
    code_match=re.search(r'```\n(.*?)\n```', llm_output, re.DOTALL)
    
    if match_p:
        code = match_p.group(1)
        description=llm_output[:match_p.start()] + llm_output[match_p.end():]
        return "python", code,description
    elif match_j:
        code = match_j.group(1)
        description=llm_output[:match_j.start()] + llm_output[match_j.end():]
        return "javascript", code,description
    elif code_match:
        # for now if the the code output does not match with either javascript or python it defaults to python 
        code = code_match.group(1)
        description=llm_output[:code_match.start()] + llm_output[code_match.end():]
        return "python", code,description
    #to match output of mistral 
    elif re.search(r'```',llm_output,re.DOTALL):

        def split_end(match,code_string):
            return code_string[match.end():]
        
        def contruct_desc(code_index,complete_text):
            desc=""
            for i,content in enumerate(complete_text):
                if(i ==code_index):
                    continue
                else:
                    desc+=content
            return desc
        
        # match_hf=re.search(r'```', llm_output, re.DOTALL)
        # code_block=llm_output[match_hf.group(1).start(): match_hf.group(2).start()]
        # match_p=re.search(r'python',code_block,re.DOTALL)

        temp=llm_output.split("```")
        code=None
        lang='python'
        desc=""
        for index,i in enumerate(temp):
            
            #skip any empty blocks from the llm_output
            if re.match(r'^[ \n]+$', i):
                continue

            match_j=re.search(r'(\bjavascript\b)',i,re.DOTALL)
            match_p=re.search(r'(\bpython\b)',i,re.DOTALL)
            if match_j:
                lang='javascript'
                code=split_end(match_j,i)
                desc=contruct_desc(index,temp)
            elif match_p:
                lang='python'
                code=split_end(match_p,i)
                desc=contruct_desc(index,temp)
            else:
                # assume python if no language matches 
                lang='python'
                code=i
                desc=contruct_desc(index,temp)
            
            if len(temp)==1:
                break
        return lang, code,desc
        
    print('regex did not match')
    return "false",None,llm_output
    

    
if __name__ == "__main__":
    llm_output = """
        Here's a simple python program that adds two numbers, squares the result, and then displays the final result:
        ```python
        def add_and_square(num1, num2):
            sum_result = num1 + num2
            return sum_result * sum_result

        # Test the function
        result = add_and_square(2, 3)
        print("The result is:", result)
        ```
        """

    llm_output = """
        Here's a simple JavaScript program that adds two numbers, squares the result, and then displays the final result:

        ``` javascript
        let num1 = 5;
        let num2 = 7;

        let sum = num1 + num2;
        let squaredResult = sum * sum;

        console.log(squaredResult);
        ```

        """
    # print(llm_output.split(r'```'))
    lang,code,desc=extract_code(llm_output)
    if lang=='python':
        print('python code \n')
        print(code)
    elif lang=='javascript':
        print('javascript code \n')
        print(code)
