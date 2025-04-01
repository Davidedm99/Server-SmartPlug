import asyncio
import json
import threading
from pathlib import Path

from starlette.requests import Request
from starlette.responses import Response

import TapoPlugs
from gui.options_window import Option
from gui.windows import MainWindow
from log_manager import init_logging
from network import Api, send_message
from options import Options

def hello_sync():
    return {'message': 'hello world'}

async def hello_async():
    return {'message': 'hello world'}

async def hello_polling(req:Request):
    body = await req.json()
    send_message(body['activityAddress'],json.dumps({'message': 'hello world'}))
    return Response('')

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


    # TODO: replace these options with the ones relevant for your application
    options = Options(AUTHOR,TITLE,[
        Option('Username', ''),
        Option('Password', ''),
        #Option('Intero', 0),
        #Option('Float', .5),
        #Option('Bool', True),
        Option('Cartella', Path.cwd()),
        Option('File', Path(__file__)),
    ])

    # Automatic discover to fill the central box
    devices = {}

    w = MainWindow(TITLE,ICON_PATH,options,ABOUT_STRINGS, devices)

    # TODO: change this line with the GUI specific to your application
    #tk.Label(w.main_frame, text="No Devices!", foreground='black', background='white').pack(expand=True, fill='both')

    # TODO: replace these API calls with the ones relevant for you
    api = Api({
        '/hello_sync': hello_sync,
        '/hello_async': hello_async,
        '/hello_polling': hello_polling,
    },port=PORT,host=HOST)
    api.start()

    w.mainloop()