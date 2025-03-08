import datetime
import os
from typing import Callable

_text = ''
_listeners: set[Callable[[str],None]] = set()

def add_listener(on_changed: Callable[[str],None])->None:
    _listeners.add(on_changed)

def add_line(line:str,sender:str=None)->None:
    global _text,_listeners
    time = f'[{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}]'
    sender = f'<{sender}>'
    line = line.strip() + os.linesep
    line = str.join(' ',[time,sender,line])

    for listener in _listeners:
        listener(line)