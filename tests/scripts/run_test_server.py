import os
import re
import socket
import subprocess
import time
from pathlib import Path


def get_open_port():
    sock = socket.socket()
    sock.bind(("", 0))
    port = str(sock.getsockname()[1])
    sock.close()
    return port


def runserver():
    p = subprocess.Popen(
        args=[
            "poetry",
            "run",
            "python",
            "-m",
            "aiohttp.web",
            "-H",
            "localhost",
            f"-P {get_open_port()}",
            "tests.mini_gql_server:init_func",
        ],
        env=os.environ.copy(),
        cwd=Path(__file__).parent.parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    while not p.stdout.readable():
        time.sleep(0.01)
        if p.stderr.readable() or p.returncode != 0:
            raise RuntimeError(p.stderr.read().decode())

    while p.stdout.readable():
        line = p.stdout.readline().decode("utf-8")
        match = re.findall(r"(Running on )(.*)( .*)", line)
        if match:
            server_address = (match[0][1] + "/graphql").replace("http", "ws")
            os.environ.setdefault("SCHEMAS_SERVER_ADDR", server_address)
            break
    p.wait()


if __name__ == "__main__":
    runserver()
