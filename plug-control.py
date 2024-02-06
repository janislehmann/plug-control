import asyncio
import os
import time
import requests
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.controller.mixins.toggle import ToggleXMixin


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


async def get_plug_power(plug: ToggleXMixin) -> float:
    power_sum = 0.0
    for _ in range(15):
        await plug.async_update()
        data = await plug.async_get_instant_metrics(channel=0)
        power_sum += data.power
        time.sleep(1)

    return round(power_sum/15, 2)


async def close_meross_session(manager: MerossManager, http_api_client: MerossHttpClient) -> None:
    manager.close()
    await http_api_client.async_logout()


def send_telegram_message(text: str) -> None:
    chatid = "-1002091987975"
    token = os.environ.get("TELEGRAM_TOKEN")

    message = f"https://api.telegram.org/{token}/sendMessage?chat_id={chatid}&text={text}"
    requests.post(message)


def read_state_file() -> str:
    with open("/home/pi/code/plug-control/state.txt", "r") as file:
        state = file.read()
    file.close()
    return state


def write_state_file(new_state: str) -> None:
    with open("/home/pi/code/plug-control/state.txt", "w") as file:
        file.write(new_state)
    file.close()


async def main():
    previous_washing_machine_state = read_state_file()
    power_threshold = 20

    manager, http_api_client = await init_meross_session()

    # try:
    plug = await get_desired_plug(manager, "Waschmaschine")

    # except:
    #     await close_meross_session(manager, http_api_client)
        
    plug_power = await get_plug_power(plug)
    print(plug_power)

    if previous_washing_machine_state == "inactiv" and plug_power > power_threshold:
        print("Washing machine is now running")
        send_telegram_message("Ich habe mit dem Waschen begonnen 🧺🛁")
        write_state_file("active")

    elif previous_washing_machine_state == "active" and plug_power < power_threshold:
        print("Washing machine has been finished")
        send_telegram_message("Ich bin fertig mit der Wäsche 👕✨")
        write_state_file("inactiv")

    elif previous_washing_machine_state == "inactiv" and plug_power < power_threshold or previous_washing_machine_state == "active" and plug_power > power_threshold:
        print("nothing to do")

    else:
        print("It semese the state file is corrupted")
        await close_meross_session(manager, http_api_client)
        exit(1)

    await close_meross_session(manager, http_api_client)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.stop()
