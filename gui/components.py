import tkinter as tk
from typing import Callable


def bordered_panel(master:tk.Misc)->tk.Frame:
    f = tk.Frame(master,background='white',highlightbackground='light steel blue',borderwidth=0,highlightthickness=1,relief='solid',padx=5,pady=5)
    return f


def small_button(master:tk.Misc,text:str,command:Callable[[],None]=None)->tk.Button:
    b = tk.Button(master,text=text,background='alice blue',highlightcolor='cornflower blue',highlightbackground='cornflower blue',highlightthickness=1,relief='raised',command=command)
    return b


def big_button(master:tk.Misc,text:str,command:Callable[[],None]=None)->tk.Button:
    b = small_button(master,text,command)
    b.configure(pady=3)
    return b
