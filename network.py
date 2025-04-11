import logging
from pathlib import Path
from threading import Thread
from typing import Callable, Awaitable

import requests
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

_FILENAME = Path(__file__).name


def send_message(address: str, payload: str):
    logging.debug(f'Sending message to {address}: {payload}')
    try:
        res = requests.post(address, json=payload)
        logging.debug(f'{res.status_code}: {res.text}')
    except Exception as e:
        logging.debug(f'Error: {e}')


class Api:
    def __init__(self, routes: dict[str, Callable[[Request], Awaitable[Response] | Response]], port: int,
                 host='127.0.0.1') -> None:
        self.app = FastAPI()
        self.port = port
        self.host = host
        self._thread: Thread | None = None

        for route, func in routes.items():
            self.app.add_route(route, func, methods=["POST"])

    def _run_blocking(self):
        logging.info(f'Listening on {self.host}:{self.port}')
        uvicorn.run(self.app, host=self.host, port=self.port, reload=False)

    def start(self):
        """Start the FastAPI application using uvicorn in the background"""
        self._thread = Thread(target=self._run_blocking, daemon=True, name='Api')
        self._thread.start()


if __name__ == '__main__':
    from log_manager import init_logging

    print(_FILENAME)
    init_logging()
    Api({}, 7071)._run_blocking()
