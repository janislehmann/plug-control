import asyncio
import os
import time
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.controller.mixins.toggle import ToggleXMixin
from datetime import datetime

async def init_meross_session() -> tuple[MerossManager, MerossHttpClient]:
    email = os.environ.get("MEROSS_EMAIL")
    password = os.environ.get("MEROSS_PASSWORD")

    http_api_client = await MerossHttpClient.async_from_user_password(api_base_url='https://iotx-eu.meross.com', email=email, password=password)
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()
    return manager, http_api_client

async def get_desired_plug(manager: MerossManager, name_of_desired_plug: str) -> ToggleXMixin:
    await manager.async_device_discovery()
    available_plugs = manager.find_devices(device_type="mss315")
    
    for plug in available_plugs:
        await plug.async_update()
        if plug.name == name_of_desired_plug:
            await plug.async_update()
            return plug
        else:
            raise Exception(f"No plug with name {name_of_desired_plug} found")

async def get_plug_data(plug: ToggleXMixin) -> float:
    data = await plug.async_get_instant_metrics(channel=0)
    return data

async def close_meross_session(manager: MerossManager, http_api_client: MerossHttpClient) -> None:
    manager.close()
    await http_api_client.async_logout()
 

def write_state_file(data: str) -> None:
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    output = f"{date};POWER;{data.power};VOLTAGE;{data.voltage};CURRENT;{data.current}\n"
    print(output)
    with open("/home/pi/code/plug-control/data/data.csv", "a") as file:
        file.write(output)
    file.close()

async def main():

    manager, http_api_client = await init_meross_session()

    plug = await get_desired_plug(manager, "Waschmaschine")

        
    for i in range(10800):
        await plug.async_update()
        data = await get_plug_data(plug)
        write_state_file(data)
        time.sleep(1.0)


    await close_meross_session(manager, http_api_client)
    


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.stop()