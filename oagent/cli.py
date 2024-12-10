import asyncclick as click
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
import ollama
import os
from . import funk
from datetime import datetime
from textwrap import dedent
import yaml

style = Style([
    ('prompt', 'ansiyellow'),     # Dim style for prompt
    ('', 'ansiyellow'),           # Dim color for user input
])

# Import rich components for styling console output
from rich.console import Console

MODEL = os.getenv('MODEL', 'llama3.1')
LOG_DIR = os.getenv('LOG_DIR', 'tmp')
REPL_HISTORY = os.path.join(LOG_DIR, '.chat_history')

style = Style([
    ('prompt', 'ansiyellow'),     # Dim style for prompt
    ('', 'ansiyellow'),           # Dim color for user input
])

session = PromptSession(history=FileHistory(REPL_HISTORY), style=style)

console = Console(file=open('/dev/tty', 'a'))  # Initialize the Console instance for rich styling

tool_dict = funk.ALL.copy()

async def handle_tools_call(messages, tool) -> list:
    console.log(f"calling function: {tool.function})", style="cyan")
    if function_to_call := tool_dict.get(tool.function.name, None):
        parts = []
        with console.status(f"[green]Executing {tool.function.name} ...") as status:
            async for line in function_to_call(**tool.function.arguments):
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

    console.log(response.message.content)
    return response

@click.command()
@click.argument('question', nargs=-1, required=True)
@click.option('--model', default=MODEL, help='The model to use')
@click.option('--no-repl', is_flag=True, help='Use REPL', default=False)
async def main(question, model=MODEL, no_repl=False):
    await run(question, model, no_repl)

async def run(question, model=MODEL, no_repl=False):
    os.makedirs(LOG_DIR, exist_ok=True)
    session = PromptSession(history=FileHistory(REPL_HISTORY), style=style)

    current_date = datetime.now().isoformat()

    log_file = os.path.join(LOG_DIR, f"messages-{current_date}.md")

    question = ' '.join(question)

    console.log(f"[bold yellow]{question}")
    messages = [
        {
            "role": "system",
            "content": \
f"""\
You are Linus Torvalds, the creator of Linux, 10x engineer, and extremely terse.

Process {{
- You answer questions by breaking them down into discrete steps
- You can use the following tools: {', '.join(tool_dict.keys())}
- `shell` is your favorite tool
- After showing the final answer, you must say `/TERMINATE` to end the conversation!
}}
Context {{
- Today is {current_date}
}}
""",
        },
        {"role": "user", "content": question},
    ]

    while True:
        response = reply(messages, model, log_file)

        while response.message.tool_calls:
            messages.append(response.message)

            for tool in response.message.tool_calls:
                messages = await handle_tools_call(messages, tool)

            response = reply(messages, model, log_file)

        if '/TERMINATE' in response.message.content:
            if no_repl:
                # remove the /TERMINATE command from the final output, and print it
                content = response.message.content.replace('/TERMINATE', '').strip()
                print(content, flush=True)
                return content
            else:
                text = await session.prompt_async("> ", style=style)
                if not text:
                    break
                messages.append({"role": "user", "content": text})

if __name__ == "__main__":
    main(_anyio_backend='asyncio')  # type: ignore
