import asyncio
import os
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
import requests

async def init_meross_session() -> tuple[MerossManager, MerossHttpClient]:
    email = os.environ.get("MEROSS_EMAIL")
    password = os.environ.get("MEROSS_PASSWORD")

    http_api_client = await MerossHttpClient.async_from_user_password(api_base_url='https://iotx-eu.meross.com', email=email, password=password)
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()
    return manager, http_api_client

async def get_desired_plug(manager: MerossManager, name_of_desired_plug: str) -> any:
    await manager.async_device_discovery()
    available_plugs = manager.find_devices(device_type="mss315")
    for plug in available_plugs:
        if plug.name == name_of_desired_plug:
            await plug.async_update()
            return plug

async def get_plug_current(plug) -> float:
    data = await plug.async_get_instant_metrics(channel=0)
    print(data)
    return data.current

async def close_meross_session(manager: MerossManager, http_api_client: MerossHttpClient) -> None:
    manager.close()
    await http_api_client.async_logout()
 
def send_message(text: str) -> None:
    chatid = "964534700"
    token = os.environ.get("TELEGRAM_TOKEN")

    message = f"https://api.telegram.org/{token}/sendMessage?chat_id={chatid}&text={text}"
    requests.post(message)

def read_state_file() -> str:
    with open("state.txt", "r") as file:
        state = file.read()
    file.close()
    return state

def write_state_file(new_state: str) -> None:
    with open("state.txt", "w") as file:
        file.write(new_state)
    file.close()

async def main():
    previous_washing_machine_state = read_state_file()
    current_threshold = 0.1

    manager, http_api_client = await init_meross_session()
    plug = await get_desired_plug(manager, "Waschmaschine")
    plug_current = await get_plug_current(plug)


    if previous_washing_machine_state == "inactiv" and plug_current > current_threshold:
        print("Washing machine is now running")
        send_message("Ich habe mit dem Waschen begonnen 🤖")
        write_state_file("active")

    elif previous_washing_machine_state == "active" and plug_current < current_threshold:
        print("Washing machine has been finished")
        send_message("Ich bin fertig mit der Wäsche 👕")
        write_state_file("inactiv")
    
    elif previous_washing_machine_state == "inactiv" and plug_current < current_threshold or previous_washing_machine_state == "active" and plug_current > 5:
        print("nothing to do")

    else:
        print("something went wrong")
        # todo: check what to do here

    await close_meross_session(manager, http_api_client)
    


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.stop()