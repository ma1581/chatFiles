import re
import subprocess


def run_python_code(input_code):
    try:
        process = subprocess.Popen(['python', '-c', input_code], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        output, error = process.communicate()
        if process.returncode == 0:
            return f"{output}"
        else:
            return f"Error:\n{error}"
    except Exception as e:
        return f"An error occurred: {e}"


def run_javascript_code(input_code):
    try:
        process = subprocess.Popen(['nodejs', '-e', input_code], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)

        output, error = process.communicate()

        if process.returncode == 0:
            return f"{output}"
        else:
            return f"Error:\n{error}"
    except Exception as e:
        return f"An error occurred: {e}"


def extract_code(llm_output):
    match_p = re.search(r'```\s*python\n(.*?)\n```', llm_output, re.DOTALL)
    match_j = re.search(r'```\s*javascript\n(.*?)\n```', llm_output, re.DOTALL)
    code_match = re.search(r'```\n(.*?)\n```', llm_output, re.DOTALL)

    if match_p:
        code = match_p.group(1)
        description = llm_output[:match_p.start()] + llm_output[match_p.end():]
        return "python", code, description
    elif match_j:
        code = match_j.group(1)
        description = llm_output[:match_j.start()] + llm_output[match_j.end():]
        return "javascript", code, description
    elif code_match:
        code = code_match.group(1)
        description = llm_output[:code_match.start()] + llm_output[code_match.end():]
        return "python", code, description
    elif re.search(r'```', llm_output, re.DOTALL):

        def split_end(match, code_string):
            return code_string[match.end():]

        def contruct_desc(code_index, complete_text):
            desc = ""
            for i, content in enumerate(complete_text):
                if (i == code_index):
                    continue
                else:
                    desc += content
            return desc

        temp = llm_output.split("```")
        code = None
        lang = 'python'
        desc = ""
        for index, i in enumerate(temp):

            if re.match(r'^[ \n]+$', i):
                continue

            match_j = re.search(r'(\bjavascript\b)', i, re.DOTALL)
            match_p = re.search(r'(\bpython\b)', i, re.DOTALL)
            if match_j:
                lang = 'javascript'
                code = split_end(match_j, i)
                desc = contruct_desc(index, temp)
            elif match_p:
                lang = 'python'
                code = split_end(match_p, i)
                desc = contruct_desc(index, temp)
            else:
                lang = 'python'
                code = i
                desc = contruct_desc(index, temp)

            if len(temp) == 1:
                break
        return lang, code, desc

    print('regex did not match')
    return "false", None, llm_output
