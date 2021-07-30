import logging
import os
import socket
import time

logging.basicConfig(level=logging.INFO)


def ping(host: str, port: int) -> None:
    addr = f"{host}:{port}"
    logging.info("Waiting for %s", addr)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        while True:
            try:
                sock.connect((host, port))
            except OSError:
                logging.error("[%s] is not responding...", addr)
                time.sleep(0.5)
            else:
                logging.info("Connection established [%s]", addr)
                break


if __name__ == "__main__":
    ping(os.environ["REDIS_HOST"], int(os.environ["REDIS_PORT"]))
    ping(os.environ["ELASTIC_HOST"], int(os.environ["ELASTIC_PORT"]))
