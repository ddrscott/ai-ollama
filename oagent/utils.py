import os
import logging
import asyncio
from typing import AsyncGenerator

async def aexecute_shell(script_content: str, timeout: int = 600) -> AsyncGenerator[str, None]:
    logger = logging.getLogger(__name__)
    shell_cmd = f"timeout {timeout} bash -e"
    logger.info(f"Shell runner command: {shell_cmd}")

    # safe env vars
    safe_env_keys = ['HOME', 'PATH', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TOGETHER_API_KEY', 'USER_WWW']
    safe_env = {k: v for k, v in os.environ.items() if k in safe_env_keys}

    from asyncio.subprocess import PIPE

    process = await asyncio.create_subprocess_shell(
        shell_cmd,
        env=safe_env,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )

    script_bytes = script_content.encode('utf-8')
    process.stdin.write(script_bytes)  # type: ignore
    await process.stdin.drain()        # type: ignore
    process.stdin.close()              # type: ignore

    async def read_stream(stream):
        while line := await stream.readline():
            yield line.decode('utf-8')

    async for line in read_stream(process.stdout):
        yield line

    async for line in read_stream(process.stderr):
        yield line

    await process.wait()
    if process.returncode == 124:
        yield f'\n[returncode:{process.returncode}]-timeout]'
    elif process.returncode != 0:
        yield f'\n[returncode:{process.returncode}]'


def execute_shell(script_content: str):
    gen = aexecute_shell(script_content)
    loop = asyncio.get_event_loop()
    try:
        while True:
            yield loop.run_until_complete(gen.__anext__()) # type: ignore
    except StopAsyncIteration:
        pass

async def aexecute_cmd(cmd, *args) -> AsyncGenerator[str, None]:
    # safe env vars
    safe_env_keys = ['HOME', 'PATH', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TOGETHER_API_KEY', 'USER_WWW']
    safe_env = {k: v for k, v in os.environ.items() if k in safe_env_keys}

    from asyncio.subprocess import PIPE

    process = await asyncio.create_subprocess_exec(
        cmd,
        *args,
        env=safe_env,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )

    async def read_stream(stream):
        while line := await stream.readline():
            yield line.decode('utf-8')

    async for line in read_stream(process.stdout):
        yield line

    async for line in read_stream(process.stderr):
        yield line

    await process.wait()
    if process.returncode == 124:
        yield f'\n[returncode:{process.returncode}]-timeout]'
    elif process.returncode != 0:
        yield f'\n[returncode:{process.returncode}]'


def execute_cmd(cmd, *args):
    gen = aexecute_cmd(cmd, *args)
    loop = asyncio.get_event_loop()
    try:
        while True:
            yield loop.run_until_complete(gen.__anext__()) # type: ignore
    except StopAsyncIteration:
        pass
