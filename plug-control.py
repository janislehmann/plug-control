import asyncio
import os
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from datetime import datetime

EMAIL = os.environ.get('MEROSS_EMAIL')
PASSWORD = os.environ.get('MEROSS_PASSWORD')

today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

async def main():

    http_api_client = await MerossHttpClient.async_from_user_password(api_base_url='https://iotx-eu.meross.com',
                                                                      email=EMAIL, 
                                                                      password=PASSWORD)
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    await manager.async_device_discovery()
    available_plugs = manager.find_devices(device_type="mss315")
    

    for plug in available_plugs:
        if plug.name == "Waschmaschine":
            dev = plug
    
    await dev.async_update()
    data = await dev.async_get_instant_metrics(channel=0)

    plug_current = data.current
    print(plug_current)

    if plug_current < 0.1:
        print("Waschmaschine aus")
    else:
        print("Waschmaschine an")

    
    manager.close()
    await http_api_client.async_logout()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.stop()