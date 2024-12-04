import ollama
from . import utils
from textwrap import dedent

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
    for part in ollama.chat('llama3.2', messages=messages, stream=True):
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


ALL = {
    'shell': shell,
    'search': search,
    'eval_python': eval_python,
    'web_text': web_text,
}
