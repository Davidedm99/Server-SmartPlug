import threading
import tkinter as tk

from log_manager import init_logging
from network import Api
from gui.windows import MainWindow




if __name__ == '__main__':
    PORT = 8080
    HOST = '127.0.0.1'

    threading.current_thread().name = "Main"
    init_logging()

    w = MainWindow('Titolo di prova','icon.ico')
    tk.Label(w.main_frame, text="Change me!", foreground='red', background='yellow').pack(expand=True, fill='both')

    api = Api({},port=PORT,host=HOST)
    api.start()

    w.mainloop()