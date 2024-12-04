import ollama
from . import utils
from textwrap import dedent

async def shell(script):
    """
    Execute a shell script in a sandboxed environment.

    Args:
      script (str): The shell script to execute

    Returns:
      stdout (str): The standard output of the script
    """

    async for line in utils.aexecute_shell(script):
        yield line

async def search(query):
    """
    Search DuckDuckGo for a query.

    Args:
      query (str): The search query

    Returns:
      results (str): The search results
    """

    lines = [line async for line in utils.aexecute_cmd('duckduckgo', query)]
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
    for part in ollama.chat('llama3.2', messages=messages, stream=True):
        if content := part['message']['content']:
            yield content

async def eval_python(expression):
    """
    Evaluate a Python script and print the results.
    Only printed results will be read!

    Args:
      expression (str): The Python expression to evaluate

    Returns:
      result (str): Printed output from the script.
    """

    async for line in utils.aexecute_cmd('python', '-c', expression):
        yield line

async def web_text(url):
    """
    Get the text of a webpage.

    Args:
      url (str): The URL of the webpage

    Returns:
      text (str): The text of the webpage
    """
    async for line in utils.aexecute_cmd('w3m', '-dump', '-cols', '9999', '-F', '-m', url):
        yield line


ALL = {
    'shell': shell,
    'search': search,
    'eval_python': eval_python,
    'web_text': web_text,
}
