import click
import ollama
import os
from . import funk
from datetime import datetime
from textwrap import dedent
import yaml

# Import rich components for styling console output
from rich.console import Console
from rich.text import Text

MODEL = os.getenv('MODEL', 'llama3.1')
LOG_DIR = os.getenv('LOG_DIR', 'tmp')

console = Console()  # Initialize the Console instance for rich styling

tool_dict = funk.ALL.copy()

def handle_tools_call(messages, tool):
    console.log( f"calling function: {tool.function})", style="cyan")
    if function_to_call := tool_dict.get(tool.function.name, None):
        parts = []
        with console.status(f"[green]Executing {tool.function.name} ...") as status:
            for line in function_to_call(**tool.function.arguments):
                parts.append(line)
                status.update(f"[green]{''.join(parts)}")

            output = "".join(parts)

            if not output.strip():
                output = "The tool had no output! Try the tool again and print the result to stdout!"
                console.log(output, style="red")
            else:
                console.log(output, style="green")
    else:
        output = f"Function {tool.function.name} not found! Available tools: {', '.join(tool_dict.keys())}"
        console.log(output, style="red")

    return messages + [{ "role": "tool", "content": str(output), "name": tool.function.name}]

def reply(messages, model, log_file):
    with console.status("thinking..."):
        response = ollama.chat(model, messages=messages, tools=tool_dict.values())

    with open(log_file, "w") as f:
        f.write('---\n')
        f.write(yaml.dump(dict(model=model, messages=messages)))
        f.write('---\n')
        f.write(response.message.content)

    console.log(f"{Text(response.message.content, style='bold green')}")
    return response

@click.command()
@click.argument('question', nargs=-1, required=True)
@click.option('--model', default=MODEL, help='The model to use')
def run(question, model=MODEL):
    os.makedirs(LOG_DIR, exist_ok=True)

    current_date = datetime.now().isoformat()

    log_file = os.path.join(LOG_DIR, f"messages-{current_date}.md")

    question = ' '.join(question)

    console.log(f"[bold yellow]{question}")
    messages = [
        {
            "role": "system",
            "content": dedent(f"""
                You are a linux administrator skilled with terminal commands and python scripting.
                You always search for the latest information and use Python for computation and print results to stdout.
                All scripts must print to stdout for the result to get captured!

                Current Date Time: {current_date}
            """),
        },
        {"role": "user", "content": question},
    ]
    response = reply(messages, model, log_file)

    while response.message.tool_calls:
        messages.append(response.message)

        for tool in response.message.tool_calls:
            messages = handle_tools_call(messages, tool)

        response = reply(messages, model, log_file)

if __name__ == "__main__":
    run()
