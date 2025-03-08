import logging
from typing import Callable

_listeners: set[Callable[[str],None]] = set()

def add_listener(on_changed: Callable[[str],None])->None:
    _listeners.add(on_changed)

class ForwardToConsole(logging.Handler):
    def handle(self, record):
        record = self.filter(record)
        if not record:
            return
        record = self.format(record)
        for listener in _listeners:
            listener(record)


def init_logging():

    logging.basicConfig(level=logging.DEBUG,format="[%(asctime)s - %(threadName)s - %(filename)s %(funcName)s] %(levelname)s - %(message)s")
    logger = logging.getLogger()

    # StdOut
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # File
    fh = logging.FileHandler('test.log') #TODO
    logger.addHandler(fh)

    # GUI
    gh = ForwardToConsole()
    gh.setLevel(logging.INFO)
    gh.setFormatter(logging.Formatter("[%(asctime)s - %(threadName)s] %(message)s"))
    logger.addHandler(gh)