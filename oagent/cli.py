import click
import ollama
import os
from . import funk
from textwrap import dedent

C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_CYAN = "\033[96m"
C_CLEAR = "\033[0m"

MODEL = os.getenv('MODEL', 'llama3.1')

tool_dict = funk.ALL.copy()

import sys
from datetime import datetime

@click.command()
@click.argument('question', nargs=-1, required=True)
@click.option('--model', default=MODEL, help='The model to use')
def run(question, model=MODEL):
    question = ' '.join(question)
    print(f'{C_YELLOW}{question}{C_CLEAR}')
    messages=[
        {'role': 'system', 'content': dedent(f"""
         You are a linux administrator skilled with terminal commands and python scripting.
         You always search for the latest information and use Python to compute results.
         All scripts must print to stdout for the result to get captured!
         The current date time is {datetime.now().isoformat()}
         """)},
        {'role': 'user', 'content': question},
    ]

    response = ollama.chat(
        model,
        messages=messages,
        tools=tool_dict.values(), # type: ignore
    )
    print(response.message.content)

    while response.message.tool_calls:
        messages.append(response.message)  # type: ignore

        for tool in response.message.tool_calls:
            print("---")
            if function_to_call := tool_dict.get(tool.function.name, None):
                print(f'{C_CYAN}> calling function: {tool.function.name }({ tool.function.arguments }) <{C_CLEAR}')
                parts = []
                for line in function_to_call(**tool.function.arguments):
                    parts.append(line)
                    print(f'{C_GREEN}{line}{C_CLEAR}', end='')
                output = (''.join(parts)).strip()
                if not output:
                    output = 'No output! Please try again. Make sure to print the answer to stdout.'
                    print(f'{C_RED}{output}{C_CLEAR}')
                else:
                    print()

                messages.append({'role': 'tool', 'content': str(output), 'name': tool.function.name}) # type: ignore
            else:
                output = f'Function {tool.function.name} not found! Available tools: {", ".join(tool_dict.keys())}'
                print(f'{C_RED}{output}{C_CLEAR}')
        response = ollama.chat(model, messages=messages, tools=tool_dict.values())  # type: ignore

    print("---")
    print(response.message.content)

if __name__ == '__main__':
    run()
