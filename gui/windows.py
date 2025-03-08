import tkinter as tk
import pyperclip
from PIL import Image, ImageTk

from gui.components import bordered_panel, big_button, small_button
from console import add_listener as on_log_text, add_line as add_console_line

class MainWindow(tk.Tk):
    main_frame: tk.Frame


    def _add_console_line(self, line:str):
        self.console_text.configure(state='normal')
        self.console_text.insert(tk.END,line)
        self.console_text.configure(state='disabled')
        if self.console_autoscroll.get():
            self.console_text.see(tk.END)

    def show_options(self):
        add_console_line('abc')
        print(type(self.console_autoscroll.get()))

    def show_about(self):
        x,y = self.winfo_pointerxy()
        about = tk.Toplevel()
        about.geometry(f"+{x}+{y}")
        about.iconbitmap(self.icon_path)
        about.title("About")
        about.configure(padx=30,pady=20,background='white',highlightcolor='cornflower blue',highlightbackground='cornflower blue',highlightthickness=1,relief='solid')
        about.overrideredirect(True)
        about.resizable(False, False)

        title_frame = tk.Frame(about,background='white')
        image = Image.open(self.icon_path)
        image = image.resize((64,64))
        tk_image = ImageTk.PhotoImage(image)
        label = tk.Label(title_frame, image=tk_image,background='white')
        label.image = tk_image
        label.pack(side='left',pady=20)
        tk.Label(title_frame, text=self.title(),font=('Segoe UI',16),background='white').pack(side=tk.LEFT,padx=20)
        title_frame.pack()
        with open('metadata.txt','r',encoding='utf-8') as f:
            for l in f:
                tk.Label(about,text=l.strip(),background='white').pack(pady=0)

        ok = small_button(about,'Ok',command=about.destroy)
        ok.configure(width=20)
        ok.pack(pady=10)


    def _clear_console(self):
        self.console_text.configure(state='normal')
        self.console_text.delete('1.0',tk.END)
        self.console_text.configure(state='disabled')

    def _copy_console(self):
        pyperclip.copy(self.console_text.get('1.0',tk.END))

    def __init__(self,title:str,icon_path:str):
        tk.Tk.__init__(self)
        # Window properties
        self.title(title)
        self.iconbitmap(icon_path)
        self.icon_path = icon_path
        self.minsize(600,400)
        self.geometry('600x400')
        self.configure(background='white',padx=10,pady=5)
        self.columnconfigure(0,weight=1)
        self.console_autoscroll = tk.BooleanVar(value=True)

        # About and options
        header_frame = bordered_panel(self)
        #tk.Label(header_frame,text="Testo di prova",compound="left").pack()
        big_button(header_frame,"About",command=self.show_about).grid(row=0,column=0)
        big_button(header_frame,"Options",command=self.show_options).grid(row=0,column=2)
        header_frame.columnconfigure(1,minsize=5)
        header_frame.grid(row=0,sticky='nw',pady=5)

        # Application-specific panel
        self.main_frame = bordered_panel(self)
        self.rowconfigure(1,weight=4)
        self.main_frame.grid(row=1,sticky='nwes',pady=5)

        # Console
        console_frame = bordered_panel(self)
        console_frame.columnconfigure(0, weight=1)
        console_frame.columnconfigure(1, weight=0)
        console_frame.rowconfigure(0, weight=1)

        console_text_frame = tk.Frame(console_frame)
        self.console_text = tk.Text(console_text_frame,state=tk.DISABLED,height=0,width=0,highlightbackground='cornflower blue',relief='solid',borderwidth=0,highlightthickness=1)
        self.console_text.pack(side='left',fill=tk.BOTH,expand=True)
        scroll = tk.Scrollbar(console_text_frame,orient='vertical',command=self.console_text.yview)
        scroll.pack(side='left',fill=tk.Y,after=self.console_text)
        self.console_text.configure(yscrollcommand=scroll.set)
        on_log_text(self._add_console_line)
        console_text_frame.grid(column=0,row=0,sticky='NSEW')

        console_frame.columnconfigure(1,minsize=5)

        console_controls = tk.Frame(console_frame,background='white')
        console_copy = small_button(console_controls,"Copy", command=self._copy_console)
        console_clear = small_button(console_controls,"Clear", command =self._clear_console)

        console_autoscroll = tk.Checkbutton(console_controls,text="Auto scroll",variable=self.console_autoscroll,background='white')

        console_copy.configure(width=15)
        console_copy.pack(fill='x')
        console_clear.pack(fill='x',pady=5)
        console_autoscroll.pack(fill='x')
        console_controls.grid(column=2,row=0,sticky='NEW')

        self.rowconfigure(2,weight=1)
        console_frame.grid(row=2,sticky='NSEW',pady=5)




if __name__ == '__main__':
    w = MainWindow('Titolo di prova','icon.ico')
    tk.Label(w.main_frame, text="Change me!", foreground='red', background='yellow').pack(expand=True, fill='both')

    w.mainloop()