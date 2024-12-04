# Ollama Agent CLI

A simple Agentic CLI based on Ollama client.

Use Ollama environment variables to change where your local server is running.


## Installation
```sh

pip install uv

uv pip install -e .
```


## Docker

```
docker build . -t ai-ollama && docker run -it --rm -e OLLAMA_HOST=http://192.168.86.35:11434 -e MODEL=qwen2.5:14b -v ${PWD}:/app $_ oagent
```
