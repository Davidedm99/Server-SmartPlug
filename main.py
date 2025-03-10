import threading
import tkinter as tk
from pathlib import Path

from gui.options import OptionsGUI, Option
from log_manager import init_logging
from network import Api
from gui.windows import MainWindow




if __name__ == '__main__':
    PORT = 8080
    HOST = '127.0.0.1'
    APP_TITLE = 'Titolo di prova'

    threading.current_thread().name = APP_TITLE
    init_logging()


    w = MainWindow(APP_TITLE,'icon.ico')

    OptionsGUI.set_defaults(default_values=[
        Option('Stringa','aaa'),
        Option('Intero',0),
        Option('Float',.5),
        Option('Bool',True),
        Option('Cartella',Path.cwd()),
        Option('File',Path(__file__)),
    ])
    OptionsGUI.load_options(APP_TITLE)
    tk.Label(w.main_frame, text="Change me!", foreground='red', background='yellow').pack(expand=True, fill='both')

    api = Api({},port=PORT,host=HOST)
    api.start()

    w.mainloop()