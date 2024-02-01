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
            return f"Output:\n{output}"
        else:
            return f"Error:\n{error}"
    except Exception as e:
        return f"An error occurred: {e}"
    

def run_javascript_code(input_code):
    try:
        # Create subprocess
        process = subprocess.Popen(['node', '-e', input_code],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)

        # Capture output and errors
        output, error = process.communicate()

        # Check if the subprocess was successful
        if process.returncode == 0:
            return f"Output:\n{output}"
        else:
            return f"Error:\n{error}"
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    st.title("Python Code Executor")

    # Input box for Python code
    python_code = st.text_area("Enter javascript Code:", "", height=100)

    if st.button("Run Code"):
        # Display Python output
        output = run_javascript_code(python_code)
        st.text_area("Python Output:", output, height=100)

if __name__ == "__main__":
    main()


import re


llm_output = """
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



def extract_code(llm_output):
    match_p = re.search(r'```\s*python\n(.*?)\n```', llm_output, re.DOTALL)
    match_j=re.search(r'```\s*javascript\n(.*?)\n```', llm_output, re.DOTALL)
    
    if match_p:
        code = match_p.group(1)
        return "python", code
    elif match_j:
        code = match_j.group(1)
        return "javascript", code
    print('regex did not match')
    
lang,code=extract_code(llm_output)
if lang=='python':
    print('python code \n')
    print(code)
elif lang=='javascript':
    print('javascript code \n')
    print(code)




#write a simple javascript program which adds two numbers and squares it  . if the code is python the format of the code : ~~~ python  \n code comes here \n ~~~ . if the code is javascript the format of the code : ~~~ javascript \n code comes here \n ~~~ . the code within the indent block must be valid