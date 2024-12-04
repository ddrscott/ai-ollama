import click
import ollama
import os
from . import funk
from datetime import datetime
from textwrap import dedent

# Import rich components for styling console output
from rich.console import Console
from rich.text import Text

MODEL = os.getenv('MODEL', 'llama3.1')

tool_dict = funk.ALL.copy()

@click.command()
@click.argument('question', nargs=-1, required=True)
@click.option('--model', default=MODEL, help='The model to use')
def run(question, model=MODEL):
    console = Console()  # Initialize the Console instance for rich styling
    question = ' '.join(question)

    console.log(f"[bold yellow]{question}")
    with console.status("Thinking...") as status:
        messages = [
            {
                "role": "system",
                "content": dedent(
                    f"""
                    You are a linux administrator skilled with terminal commands and python scripting.
                    You always search for the latest information and use Python to compute results.
                    All scripts must print to stdout for the result to get captured!
                    The current date time is {datetime.now().isoformat()}
                    """
                ),
            },
            {"role": "user", "content": question},
        ]

        response = ollama.chat(model, messages=messages, tools=tool_dict.values())

    console.log(f"{Text(response.message.content, style='bold green')}")

    while response.message.tool_calls:
        with console.status("[green]Executing tool...") as status:
            messages.append(response.message)

            for tool in response.message.tool_calls:
                console.log(
                    f"calling function: {tool.function.name}({tool.function.arguments})", style="cyan"
                )

                if function_to_call := tool_dict.get(tool.function.name, None):
                    parts = []
                    for line in function_to_call(**tool.function.arguments):
                        parts.append(line)
                        status.update(f"[green]{''.join(parts)}")
                    output = "".join(parts)
                    if not output.strip():
                        console.log(Text("No output! Please try again. Make sure to print results to stdout.", style="red"))
                    else:
                        console.log(output, style="green")

                    messages.append(
                        {
                            "role": "tool",
                            "content": str(output),
                            "name": tool.function.name,
                        }
                    )
                else:
                    console.log(Text(f"Function {tool.function.name} not found! Available tools: {', '.join(tool_dict.keys())}", style="red"))
            response = ollama.chat(model, messages=messages, tools=tool_dict.values())

    console.log(response.message.content)

if __name__ == "__main__":
    run()
