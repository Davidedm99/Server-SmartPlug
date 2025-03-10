import json
import threading
import tkinter as tk
from pathlib import Path

from gui.options_window import Option
from gui.windows import MainWindow
from log_manager import init_logging
from network import Api
from options import Options

if __name__ == '__main__':
    with open(Path(__file__).resolve().with_name('metadata.json'),'r') as f:
        data = json.load(f)
        TITLE = data['title']
        AUTHOR = data['author']
        HOST = data['host']
        PORT = data['port']
        start, end = data['copyright']
        ABOUT_STRINGS = [
            AUTHOR,
            f'© {start}-{end}',
            f'Version: {data['version']}',
        ]
        ICON_PATH = Path(__file__).resolve().with_name('icon.ico')

    threading.current_thread().name = TITLE
    init_logging()

    options = Options(AUTHOR,TITLE,[
        Option('Stringa', 'aaa'),
        Option('Intero', 0),
        Option('Float', .5),
        Option('Bool', True),
        Option('Cartella', Path.cwd()),
        Option('File', Path(__file__)),
    ])
    w = MainWindow(TITLE,ICON_PATH,options,ABOUT_STRINGS)

    tk.Label(w.main_frame, text="Change me!", foreground='red', background='yellow').pack(expand=True, fill='both')

    api = Api({},port=PORT,host=HOST)
    api.start()

    w.mainloop()