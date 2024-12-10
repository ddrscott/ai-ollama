import ollama
from . import utils
from textwrap import dedent

async def shell(script:str):
    """
    Execute a shell script in a sandboxed environment.
    - `cat -n /path/to/source` to read files.
    - `cat <<-EOF | tee /path/to/dest` to write directly to files.
    """

    async for line in utils.aexecute_shell(script):
        yield line

async def search(query:str):
    """
    Search the internet using DuckDuckGo for one thing at a time.
    """

    lines = [line async for line in utils.aexecute_cmd('duckduckgo', query)]
    results = ''.join(lines)
    prompt = dedent(f"""
        Given the following search results:
        ---
        {results}
        ---
        Use the search results to answer the query: "{query}"
        Cite your sources with links as needed.
        """)

    messages=[{'role': 'user', 'content': prompt}]
    for part in ollama.chat('llama3.2', messages=messages, stream=True):
        if content := part['message']['content']:
            yield content

async def eval_python(script:str):
    """
    Evaluate a Python script.
    Results must be printed to stdout.
    """

    async for line in utils.aexecute_cmd('python', '-c', script):
        yield line

async def web_text(url:str):
    """
    Get the text of a webpage.
    """
    async for line in utils.aexecute_cmd('w3m', '-dump', '-cols', '9999', '-F', '-m', url):
        yield line


ALL = {
    'shell': shell,
    'search': search,
    'eval_python': eval_python,
    'web_text': web_text,
}
