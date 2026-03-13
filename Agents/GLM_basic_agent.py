from zai import ZaiClient
from dotenv import load_dotenv
import re
import subprocess
import os

load_dotenv()
client = ZaiClient()

def query_lm(messages):
    response = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=messages
    )
    return response.choices[0].message.content

def parse_action(lm_output: str) -> str:
    pattern = r"```(?:bash-action|bash|sh)\s*\n?(.*?)\n?```"
    matches = re.findall(pattern, lm_output, re.DOTALL)
    if not matches:
        return ""
    return matches[0].strip()

def execute_action(command: str) -> str:
    if not command.strip():
        return "Error: Empty command received."
    command = command.replace('\r', '').strip()
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        env=os.environ,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
    )
    return result.stdout

messages = [{
    "role": "system", 
    "content": "You are a helpful assistant. To run a bash command, wrap it in a code block like this:\n```bash-action\nls\n```\nYou can run multiple commands sequentially. When the task is complete, provide a final answer to the user. To exit, run the 'exit' command."
}]

while True:
    try:
        user_input = input("\n You: ")
        if not user_input.strip():
            continue
        messages.append({"role": "user", "content": user_input})
        while True:
            lm_output = query_lm(messages)
            if not lm_output or not lm_output.strip():
                print("\n[DEBUG]: Received empty response from model.")
                break
            messages.append({"role": "assistant", "content": lm_output})
            print("-" * 60)
            print(lm_output)
            print("-" * 60)
            action = parse_action(lm_output)
            if not action:
                break
            if action.lower() == "exit":
                print("Exiting...")
                exit()
            print(f"\n[EXECUTING]: {action}")
            output = execute_action(action)
            clean_output = output.strip() if output else "Command executed (No output)"
            print(f"[OUTPUT]:\n{clean_output}")
            messages.append({"role": "user", "content": clean_output})
    except KeyboardInterrupt:
        print("\nInterrupted by user. Goodbye!")
        break
    except Exception as e:
        error_msg = f"Error occurred: {str(e)}"
        print(f"\n[ERROR]: {error_msg}")
        if "APIRequestFailedError" not in str(e):
             messages.append({"role": "user", "content": error_msg})
        else:
            print("API Error detected. Resetting dialogue or stopping.")
            break
