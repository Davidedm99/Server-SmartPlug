import asyncio
import json
import logging
import threading
from pathlib import Path

from starlette.requests import Request
from starlette.responses import Response

from gui.options_window import Option
from gui.windows import MainWindow
from log_manager import init_logging
from network import Api, send_message
from options import Options
import tapo_plugs


async def request_handler(request: Request):
    # Read the JSON payload from the request
    response = await request.json()

    message = json.loads(response['item'][0]['request']['body']['raw'])
    msg_type = message.get("type", None)

    if msg_type == "SmartPlugDiscovery":
        await tapo_plugs.retrieve_devices()
        # TODO: what should be returned to a SmartPlugDiscovery
        return Response(content="Discovery success", status_code=200)

    elif msg_type == "SmartPlugCommand":
        command = message.get("command")
        plug_ip = w.retrieve_plug_ip(message.get("id"))
        plug = w.retrieve_plug(plug_ip)

        if plug:
            match command.lower():
                case "on":
                    await plug.turn_on()
                    w.update_buttons(plug_ip, True)
                    return Response(content=f"Plug switched {command.lower()}", status_code=200)
                case "off":
                    await plug.turn_off()
                    w.update_buttons(plug_ip, False)
                    return Response(content=f"Plug switched {command.lower()}", status_code=200)
                case _:
                    return Response(content="Missing command in SmartPlugCommand", status_code=400)
        else:
            return Response(content="Plug name not found in Middleware", status_code=400)

    else:
        return Response(content=f"Unknown message type: {msg_type}", status_code=400)


def hello_sync():
    return {'message': 'hello world'}


async def hello_async():
    return {'message': 'hello world'}


async def hello_polling(req: Request):
    body = await req.json()
    send_message(body['activityAddress'], json.dumps({'message': 'hello world'}))
    return Response('')


if __name__ == '__main__':
    with open(Path(__file__).resolve().with_name('metadata.json'), 'r') as f:
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
    options = Options(AUTHOR, TITLE, [
        Option('Username', ''),
        Option('Password', ''),
        #Option('Intero', 0),
        #Option('Float', .5),
        #Option('Bool', True),
        Option('Cartella', Path.cwd()),
        Option('File', Path(__file__)),
        Option('SavedPlugs', "{}", False),
    ])

    # Automatic discover to fill the central box
    devices = {}

    w = MainWindow(TITLE, ICON_PATH, options, ABOUT_STRINGS, devices)

    # TODO: change this line with the GUI specific to your application
    #tk.Label(w.main_frame, text="No Devices!", foreground='black', background='white').pack(expand=True, fill='both')

    # TODO: replace these API calls with the ones relevant for you
    api = Api({
        '/hello_sync': hello_sync,
        '/hello_async': hello_async,
        '/hello_polling': hello_polling,
        '/smart_plugs': request_handler,
    }, port=PORT, host=HOST)
    api.start()

    w.mainloop()
