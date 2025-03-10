import json
import json
import os
import pathlib
import tkinter as tk
from pathlib import Path
from tkinter import Variable, BooleanVar, IntVar, DoubleVar, StringVar
from tkinter.filedialog import askopenfilename, askdirectory

from platformdirs import user_config_dir

from gui.components import big_button


class Option:
    def __init__(self,name:str,value:str|Path|bool|int|float,visible=True):
        self._variable: Variable
        if isinstance(value,bool):
            self._variable = BooleanVar(value=value)
        elif isinstance(value,int):
            self._variable = IntVar(value=value)
        elif isinstance(value,float):
            self._variable = DoubleVar(value=value)
        elif isinstance(value,Path) or isinstance(value,str):
            self._variable = StringVar(value=value)

        self.name = name
        self.value = value
        self.visible = visible

    @property
    def value(self)->str|Path|bool|int|float:
        val = self._variable.get()
        try:
            path = Path(val)
            if path.exists():
                return path
        except TypeError:
            pass
        return val

    @value.setter
    def value(self,val:str|Path|bool|int|float):
        self._variable.set(val)

    def render(self,master:tk.Misc):
        if not self.visible:
            return
        f = tk.Frame(master,background='white')
        if isinstance(self.value,bool):
            tk.Checkbutton(f,text=self.name,background='white',variable=self._variable).pack(side='left')
        elif type(self.value) in (str,int,float):
            tk.Label(f,text=self.name,background='white').pack(anchor='w')
            tk.Entry(f,textvariable=self._variable).pack(expand=True, fill='x')
        elif isinstance(self.value,pathlib.Path):
            t = tk.Entry(f,textvariable=self._variable,width=0)
            t.configure(state='disabled')
            def select_file():
                if self.value.is_dir():
                    self.value = askdirectory(initialdir=os.getcwd())
                elif self.value.is_file():
                    self.value = askopenfilename(defaultextension=self.value.suffix)

            change = big_button(f,'Change path',command=select_file)
            show = big_button(f, 'Open',command=lambda:os.startfile((self.value if self.value.is_dir() else self.value.parent).as_posix()))
            t.pack(expand=True, fill='x',side='left')
            show.pack(side='right',padx=5)
            change.pack(side='right')
        else:
            raise ValueError(f'Invalid option type {type(self.value)}')
        f.pack(fill='x',pady=5,anchor='n')

    def toDict(self):
        val = str(self.value) if isinstance(self.value,Path) else self.value
        return {'name':self.name,'value':val,'visible':self.visible}
class OptionsGUI(tk.Toplevel):
    options: dict[str,Option]|None=None

    @staticmethod
    def set_defaults(default_values:list[Option]):
        OptionsGUI.options = {o.name:o for o in default_values}

    def __init__(self,master:tk.Tk):
        tk.Toplevel.__init__(self)
        # Window properties
        self.app_title = master.title()

        if OptionsGUI.options is None:
            raise ValueError('Options not initialized')

        #TODO: use a copy instead
        for option in OptionsGUI.options.values():
            option.render(self)

        # Ok and cancel
        buttons_frame = tk.Frame(self,background='white')
        ok = big_button(buttons_frame,'Ok', command=self.save_and_close)
        cancel = big_button(buttons_frame,'Cancel',command=self.destroy)
        ok.configure(width=10)
        ok.pack(side='left',padx=5)
        cancel.configure(width=10)
        cancel.pack(side='right')

        buttons_frame.pack(side='bottom',anchor='ne')

    def save_and_close(self):
        path = Path(user_config_dir(appname=self.app_title,appauthor='I3Lab',ensure_exists=True),'options.json')
        with open(path,'w') as f:
            json.dump([o.toDict() for o in OptionsGUI.options.values()], f, sort_keys=True, indent=4)
        self.destroy()

    @staticmethod
    def load_options(app_title:str):
        path = Path(user_config_dir(appauthor='I3Lab', appname=app_title), 'options.json')
        if path.exists():
            with open(path, 'r') as f:
                lst = json.load(f)
                for o in lst:
                    OptionsGUI.options[o['name']] = Option(o['name'], o['value'], o['visible'])


if __name__ == '__main__':
    root = tk.Tk()
    title='test'
    root.title(title)
    OptionsGUI.set_defaults(default_values=[
        Option('Stringa','aaa'),
        Option('Intero',0),
        Option('Float',.5),
        Option('Bool',True),
        Option('Cartella',Path.cwd()),
        Option('File',Path(__file__)),
    ])
    OptionsGUI.load_options(title)
    OptionsGUI(root)
    root.mainloop()