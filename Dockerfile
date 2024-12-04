FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
       w3m \
       jq \
       curl \
       git \
       wget \
       make \
       gawk \
       && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uv 

WORKDIR /app
COPY . .
RUN uv pip install --system -e .
COPY bin/* /usr/local/bin/
