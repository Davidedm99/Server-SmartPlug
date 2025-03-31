import threading

from kasa import Discover
import asyncio
import logging


# Kasa function to discover devices on a local network
async def discover_devices():
    # Use kasa package to do discover on broadcast
    devices = await Discover.discover()
    return devices


# Wrapper function to run the async discovery from a synchronous context
def retrieve_devices():
    return asyncio.run(discover_devices())


