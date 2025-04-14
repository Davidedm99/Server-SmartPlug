from kasa import Discover
import asyncio
import logging


class TapoPlugs:
    def __init__(self, ip: str, username: str, password: str):
        self.ip = ip
        self.username = username
        self.password = password
        self.status = False

    # For TapoP100 Authentication is needed for each command
    async def discover_self(self):
        return await Discover.discover_single(
            host=self.ip,
            username=self.username,
            password=self.password
        )

    # Update device info before display -- NEEDED AFTER EVERY ACTION --
    async def update_self(self):
        device = await self.discover_self()
        await device.update()
        self.status = device.is_on

    # Turn on the specific device
    async def turn_on(self):
        device = await self.discover_self()

        await device.turn_on()
        await device.update()
        #logging.info(device.is_on)
        await device.disconnect()

        return device.is_on

    # Turn off the specific device
    async def turn_off(self):
        device = await self.discover_self()

        await device.turn_off()
        await device.update()
        #logging.info(device.is_on)
        await device.disconnect()

        return device.is_on


# FUNCTION NOT DEVICE-DEPENDANT
# Kasa function to discover devices on a local network
async def discover_devices():
    # Use kasa package to do discover on broadcast
    devices = await Discover.discover()
    return devices


# Wrapper function to run the async discovery from a synchronous context
def retrieve_devices():
    return asyncio.run(discover_devices())