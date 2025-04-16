import asyncio
import json
import logging
import os
import threading
import tkinter as tk
from functools import partial
from typing import Dict

import pyperclip
from PIL import Image, ImageTk
from pathlib import Path

import tapo_plugs
import log_manager
from gui.components import bordered_panel, big_button, small_button
from gui.options_window import OptionsGUI
from options import Options


class MainWindow(tk.Tk):
    main_frame: tk.Frame

    def _add_console_line(self, line: str):
        self.console_text.configure(state='normal')
        self.console_text.insert(tk.END, line + os.linesep)
        self.console_text.configure(state='disabled')
        if self.console_autoscroll.get():
            self.console_text.see(tk.END)

    def show_options(self):
        options = OptionsGUI(self.options)
        options.iconbitmap(self.icon_path)
        options.transient(self)
        options.grab_set()
        self.wait_window(options)

    # Do the discovery with the kasa library
    def python_kasa(self, callback):
        devices = tapo_plugs.retrieve_devices()

        for dev in devices:
            # Create Tapo object
            plug = tapo_plugs.TapoPlugs(dev, self.options['Username'].value, self.options['Password'].value)
            # Update the device
            asyncio.run(plug.update_self())

            self.devices[dev] = plug

        callback()

    # Discovery function
    def tapo_discovery(self):
        logging.info("Discovery started...")
        self.clear_entries()
        thread = threading.Thread(target=self.python_kasa, args=(lambda: self.after(0, self.populate_frame()),),
                                  name='Discovery',
                                  daemon=True)
        thread.start()

    # Turn on or off the tapo
    def tapo_command(self, device_ip, command, callback):
        device = self.devices[device_ip]

        if command == 'on':
            asyncio.run(device.turn_on())
        else:
            asyncio.run(device.turn_off())

        callback(device.status)

    # Start the thread to turn on or off the Tapo
    def toggle_status(self, device_ip, command):

        thread = threading.Thread(target=self.tapo_command,
                                  args=(
                                        device_ip,
                                        command,
                                        lambda status: self.after(0, self.update_buttons, device_ip, status)
                                  ),
                                  name='Command',
                                  daemon=True)

        thread.start()

    # Method to update the button in the main frame based on the plug status
    # TODO: check if the status of the plug is actually updated and is not referencing to a different state or plug
    def update_buttons(self, device_ip, status):
        plug_state = 'ON' if status else 'OFF'
        logging.info(f"Plug has been turned {plug_state}")
        self.widgets[device_ip][2]['text'] = plug_state

    # Clear the central widget when discovery is started
    def clear_entries(self):
        self.label.pack_forget()
        for device_widgets in self.widgets.values():
            for widget in device_widgets:
                widget.destroy()
        self.widgets.clear()

    # Look for existing names of a relative plug in the config option and retrieve them
    def retrieve_plug_name(self, device_ip):
        data = json.loads(self.options['SavedPlugs'].value)
        if device_ip in data:
            return data[device_ip]
        else:
            return next((name for name, plug in self.devices.items() if plug.ip == device_ip), 'New Smart Plug')

    # Function to retrieve the plug object knowing the relative IP
    def retrieve_plug_ip(self, plug_name):
        saved_plugs = json.loads(self.options['SavedPlugs'].value)
        for ip, name in saved_plugs.items():
            if name == plug_name:
                return ip

    # retrieve the tapo_plug object base don the given IP
    def retrieve_plug(self, plug_ip):
        if plug_ip in self.devices:
            return self.devices[plug_ip]

    # Update the name of a plug and save it into the config for future use
    def update_name(self, event, entry, device_ip):
        # Open JSON with all the names and edit the one associated with the device ip
        data = json.loads(self.options['SavedPlugs'].value)
        data[device_ip] = entry.get()
        # Update the options value
        self.options['SavedPlugs'].value = json.dumps(data)
        Options.save(self.options)
        event.widget.master.focus_set()

        #Update the local dictionary

    # Function for populating the central part of the interface based on the return of python-kasa
    def populate_frame(self):
        if len(self.devices) == 0:
            logging.info("No device(s) found!")
            self.label = tk.Label(self.main_frame, text="No Device(s) Found!")
            self.label.pack(expand=True, fill='both')
        else:
            for i, device in enumerate(self.devices):
                self.main_frame.columnconfigure(0, weight=1)

                entry = tk.Entry(self.main_frame)
                entry.insert(0, self.retrieve_plug_name(self.devices[device].ip))
                entry.grid(row=i, column=0, padx=5, pady=2, sticky="we")

                # Rename the entry
                entry.bind("<Return>", lambda e, ent=entry, dev=self.devices[device].ip: self.update_name(e, ent, dev))

                label = tk.Label(self.main_frame, text=self.devices[device].ip)
                label.grid(row=i, column=1, padx=5, pady=2)

                button = tk.Button(
                    self.main_frame,
                    text="ON" if self.devices[device].status else "OFF",
                )

                command = 'off' if self.devices[device].status else 'on'

                button.config(command=partial(self.toggle_status, self.devices[device].ip, command))
                button.grid(row=i, column=2, padx=5, pady=2)

                #self.widgets.extend([entry, label, button])
                # save a reference to windows element relative to the device
                self.widgets[device] = ([entry, label, button])

    def show_about(self):
        x, y = self.winfo_pointerxy()
        about = tk.Toplevel()
        about.geometry(f"+{x}+{y}")
        about.iconbitmap(self.icon_path)
        about.title("About")
        about.configure(padx=30, pady=20, background='white', highlightcolor='cornflower blue',
                        highlightbackground='cornflower blue', highlightthickness=1, relief='solid')
        about.overrideredirect(True)
        about.resizable(False, False)

        title_frame = tk.Frame(about, background='white')
        image = Image.open(self.icon_path)
        image = image.resize((64, 64))
        tk_image = ImageTk.PhotoImage(image)
        label = tk.Label(title_frame, image=tk_image, background='white')
        label.image = tk_image
        label.pack(side='left', pady=20)
        tk.Label(title_frame, text=self.title(), font=('Segoe UI', 16), background='white').pack(side=tk.LEFT, padx=20)
        title_frame.pack()

        for abt in self.about:
            tk.Label(about, text=abt.strip(), background='white').pack(pady=0)

        ok = small_button(about, 'Ok', command=about.destroy)
        ok.configure(width=20)
        ok.pack(pady=10)

    def _clear_console(self):
        self.console_text.configure(state='normal')
        self.console_text.delete('1.0', tk.END)
        self.console_text.configure(state='disabled')

    def _copy_console(self):
        pyperclip.copy(self.console_text.get('1.0', tk.END))

    def __init__(self, title: str, icon_path: Path, options: Options, about: list[str], devices: Dict[str, tapo_plugs]):
        tk.Tk.__init__(self)
        # Window properties
        self.title(title)
        self.icon_path = icon_path
        self.iconbitmap(icon_path)
        self.minsize(600, 400)
        self.geometry('600x400')
        self.configure(background='white', padx=10, pady=5)
        self.columnconfigure(0, weight=1)
        self.console_autoscroll = tk.BooleanVar(value=True)
        self.options = options
        self.about = about
        self.devices = devices
        self.widgets = {}
        self.result = []
        self.label = None
        self.response = None

        # About and options
        header_frame = bordered_panel(self)
        big_button(header_frame, "About", command=self.show_about).grid(row=0, column=0)
        big_button(header_frame, "Options", command=self.show_options).grid(row=0, column=2)
        header_frame.columnconfigure(1, minsize=5)
        header_frame.grid(row=0, sticky='nw', pady=5)

        # Discovery
        discover_frame = bordered_panel(self)
        big_button(discover_frame, "Discover", command=self.tapo_discovery).grid(row=0, column=5)
        discover_frame.columnconfigure(1, minsize=5)
        discover_frame.grid(row=0, sticky='ne', pady=5)

        # Application-specific panel
        self.main_frame = bordered_panel(self)
        self.rowconfigure(1, weight=4)
        self.main_frame.grid(row=1, sticky='nwes', pady=5)

        self.label = tk.Label(self.main_frame, text="No Device(s) Found!")
        self.label.pack(expand=True, fill='both')

        # Console
        console_frame = bordered_panel(self)
        console_frame.columnconfigure(0, weight=1)
        console_frame.columnconfigure(1, weight=0)
        console_frame.rowconfigure(0, weight=1)

        console_text_frame = tk.Frame(console_frame)
        self.console_text = tk.Text(console_text_frame, state=tk.DISABLED, height=0, width=0,
                                    highlightbackground='cornflower blue', relief='solid', borderwidth=0,
                                    highlightthickness=1, wrap='none')
        self.console_text.pack(side='left', fill=tk.BOTH, expand=True)
        scroll = tk.Scrollbar(console_text_frame, orient='vertical', command=self.console_text.yview)
        scroll.pack(side='left', fill=tk.Y, after=self.console_text)
        self.console_text.configure(yscrollcommand=scroll.set)
        log_manager.add_listener(self._add_console_line)
        console_text_frame.grid(column=0, row=0, sticky='NSEW')

        console_frame.columnconfigure(1, minsize=5)

        console_controls = tk.Frame(console_frame, background='white')
        console_copy = small_button(console_controls, "Copy", command=self._copy_console)
        console_clear = small_button(console_controls, "Clear", command=self._clear_console)

        console_autoscroll = tk.Checkbutton(console_controls, text="Auto scroll", variable=self.console_autoscroll,
                                            background='white')

        console_copy.configure(width=15)
        console_copy.pack(fill='x')
        console_clear.pack(fill='x', pady=5)
        console_autoscroll.pack(fill='x')
        console_controls.grid(column=2, row=0, sticky='NEW')

        self.rowconfigure(2, weight=1)
        console_frame.grid(row=2, sticky='NSEW', pady=5)

        # Automatic discovery at startup
        self.tapo_discovery()


if __name__ == '__main__':
    from options import Option
    from pathlib import Path

    opt = Options('test', 'test', [
        Option('Stringa', 'aaa'),
        Option('Intero', 0),
        Option('Float', .5),
        Option('Bool', True),
        Option('Cartella', Path.cwd()),
        Option('File', Path(__file__)),
    ])
    w = MainWindow('test', opt, [f'About string {i}' for i in range(10)])

    w.mainloop()
