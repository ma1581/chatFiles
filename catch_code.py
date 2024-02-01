import re


llm_output = """
~~~ python
def add_and_square(num1, num2):
    sum_result = num1 + num2
    return sum_result * sum_result

# Test the function
result = add_and_square(2, 3)
print("The result is:", result)
~~~
"""


llm_output = """
 Here's a simple JavaScript program that adds two numbers, squares the result, and then displays the final result:

~~~javascript
let num1 = 5;
let num2 = 7;

let sum = num1 + num2;
let squaredResult = sum * sum;

console.log(squaredResult);
~~~

"""



def extract_code(llm_output):
    match_p = re.search(r'~~~\s*python\n(.*?)\n~~~', llm_output, re.DOTALL)
    match_j=re.search(r'~~~\s*javascript\n(.*?)\n~~~', llm_output, re.DOTALL)
    
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

