import ollama
import os
import utils
from textwrap import dedent

C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_CYAN = "\033[96m"
C_CLEAR = "\033[0m"

MODEL = os.getenv('MODEL', 'llama3.1')

def shell(script):
    """
    Execute a shell script in a sandboxed environment.

    Args:
      script (str): The shell script to execute

    Returns:
      stdout (str): The standard output of the script
    """

    yield from utils.execute_shell(script)

def search(query):
    """
    Search DuckDuckGo for a query.

    Args:
      query (str): The search query

    Returns:
      results (str): The search results
    """

    lines = [line for line in utils.execute_cmd('duckduckgo', query)]
    results = ''.join(lines)
    prompt = dedent(f"""\
        Given the following search results:
        ---
        {results}
        ---
        Use the search results to answer the query: "{query}"
        Cite your sources with links as needed.
        """)

    messages=[{'role': 'user', 'content': prompt}]
    for part in ollama.chat( MODEL, messages=messages, stream=True):
        if content := part['message']['content']:
            yield content

def eval_python(expression):
    """
    Evaluate a Python script and print the results.
    Only printed results will be read!

    Args:
      expression (str): The Python expression to evaluate

    Returns:
      result (str): Printed output from the script.
    """

    yield from utils.execute_cmd('python', '-c', expression)

def web_text(url):
    """
    Get the text of a webpage.

    Args:
      url (str): The URL of the webpage

    Returns:
      text (str): The text of the webpage
    """
    yield from utils.execute_cmd('w3m', '-dump', '-cols', '9999', '-F', '-m', url)

tool_dict = {
    'shell': shell,
    'search': search,
    'eval_python': eval_python,
    'web_text': web_text,
}

import sys
from datetime import datetime

messages=[
    {'role': 'system', 'content': dedent(f"""
     You are a linux administrator skilled with terminal commands and python scripting.
     You always search for the latest information and use Python to compute results. All scripts must print to stdout
     for the result to get captured!
     The current date time is {datetime.now().isoformat()}
     """)},
    {'role': 'user', 'content': ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'What is the current date and time?'},
]

response = ollama.chat(
    MODEL,
    messages=messages,
    tools=tool_dict.values(), # type: ignore
)

print(response.message.content)

while response.message.tool_calls:
    messages.append(response.message)  # type: ignore

    for tool in response.message.tool_calls:
        if function_to_call := tool_dict.get(tool.function.name, None):
            print(f'{C_CYAN}>>  calling function: {tool.function.name }({ tool.function.arguments }) {C_CLEAR}')
            parts = []
            for line in function_to_call(**tool.function.arguments):
                parts.append(line)
                print(f'{C_GREEN}{line}{C_CLEAR}', end='')
            print("\n---")
            output = ''.join(parts)
        else:
            print(f'Function {tool.function.name} not found in tool_dict')

        messages.append({'role': 'tool', 'content': str(output), 'name': tool.function.name}) # type: ignore

    response = ollama.chat(MODEL, messages=messages, tools=tool_dict.values())  # type: ignore

print("---")
print(response.message.content)
