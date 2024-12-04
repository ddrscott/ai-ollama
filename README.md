# Ollama Agent CLI

A simple Agentic CLI based on Ollama client.

Use Ollama environment variables to change where your local server is running.


## Installation
```sh

pip install uv

uv pip install -e .

oagent --help
```

### Install Ollama Models
```sh
# llama3.2 is required to summarize searches and web results.
ollama pull llama3.2

# qwen2.5 is the best model for general reasoning and tool composition.
ollama pull qwen2.5:14b
```


## Docker

### Use my image
```sh
# Use my docker hosted image
docker run -it --rm \
    -e OLLAMA_HOST=http://192.168.86.35:11434 \
    -e MODEL=qwen2.5:14b \
    ddrscott/oagent \
    'How much older is Tom Hanks than Tom Holland in days?'
```

### Build your own
```sh
docker build . -t oagent && \
    docker run -it --rm \
        -e OLLAMA_HOST=http://192.168.86.35:11434 \
        -v ${PWD}:/app \
        $_ --model 'qwen2.5:14b' '5 + 1 = ?, return in JSON format only'
```
