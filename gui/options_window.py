import os
import pathlib
import tkinter as tk
from pathlib import Path
from tkinter import Variable, BooleanVar, IntVar, DoubleVar, StringVar
from tkinter.filedialog import askopenfilename, askdirectory

from gui.components import big_button
from options import Options, Option


class OptionsGUI(tk.Toplevel):

    def __init__(self, options:Options):
        tk.Toplevel.__init__(self)
        self.variables: dict[str,Variable] = {}

        # Window title
        self.title('Options')
        self.geometry('600x400')
        self.configure(background='white',padx=10,pady=5)

        # Load data
        self.options = options
        for option in self.options.values():
            self.variables[option.name] = OptionsGUI.create_variable(option.value)
            self.render_option(option)

        # Ok and cancel
        buttons_frame = tk.Frame(self,background='white')
        ok = big_button(buttons_frame,'Ok', command=self.ok)
        cancel = big_button(buttons_frame,'Cancel',command=self.destroy)
        ok.configure(width=10)
        ok.pack(side='left',padx=5)
        cancel.configure(width=10)
        cancel.pack(side='right')
        buttons_frame.pack(side='bottom',anchor='ne')

    @staticmethod
    def create_variable(option_value: str | Path | bool | int | float)->Variable:
        if isinstance(option_value, bool):
            return BooleanVar(value=option_value)
        elif isinstance(option_value, int):
            return IntVar(value=option_value)
        elif isinstance(option_value, float):
            return DoubleVar(value=option_value)
        elif isinstance(option_value, Path) or isinstance(option_value, str):
            return StringVar(value=option_value)
        raise ValueError(f'Invalid option type {type(option_value)}')

    def render_option(self,option:Option):
        if not option.visible:
            return
        f = tk.Frame(self,background='white')
        variable = self.variables[option.name]

        if isinstance(option.value,bool):
            tk.Checkbutton(f,text=option.name,background='white',variable=variable).pack(side='left')
        elif type(option.value) in (str,int,float):
            tk.Label(f,text=option.name,background='white').pack(anchor='w')
            tk.Entry(f,textvariable=variable).pack(expand=True, fill='x')
        elif isinstance(option.value,pathlib.Path):
            t = tk.Entry(f,textvariable=variable,width=0)
            t.configure(state='disabled')
            def select_file():
                if option.value.is_dir():
                    option.value = askdirectory(initialdir=os.getcwd())
                elif option.value.is_file():
                    option.value = askopenfilename(defaultextension=option.value.suffix)

            change = big_button(f,'Change path',command=select_file)
            show = big_button(f, 'Open',command=lambda:os.startfile((option.value if option.value.is_dir() else option.value.parent).as_posix()))
            t.pack(expand=True, fill='x',side='left')
            show.pack(side='right',padx=5)
            change.pack(side='right')
        else:
            raise ValueError(f'Invalid option type {type(option.value)}')

        f.pack(fill='x',pady=5,anchor='n')

    def ok(self):
        for name, var in self.variables.items():
            val = var.get()
            try:
                path = Path(val)
                if path.exists():
                    val = path
            except TypeError:
                pass
            self.options[name].value = val
        self.options.save()
        self.destroy()



if __name__ == '__main__':
    root = tk.Tk()
    title='test'
    root.title(title)
    options = Options('test','test',[
        Option('Stringa','aaa'),
        Option('Intero',0),
        Option('Float',.5),
        Option('Bool',True),
        Option('Cartella',Path.cwd()),
        Option('File',Path(__file__)),
    ])
    OptionsGUI(options)
    root.mainloop()