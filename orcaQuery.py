import subprocess
import argparse
#parser=argparse.ArgumentParser()
#parser.add_argument("--q",type=str,help="This is the Query")
#args=parser.parse_args()

def query(context,ques):
    # Run an interactive Bash shell
    try:
        result = subprocess.run(['ollama', 'run', 'orca-mini'], shell=False, check=True, text=True, capture_output=True, 
        input="Context:"+context+".\n Based on Above Context Answer the below Question.\n"+ques)

        # Print the command output
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running the command: {e}")
