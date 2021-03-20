import asyncio
import base64
from typing import Tuple
import keyboard
import websockets
import time
import pyautogui
from io import BytesIO
import json
import requests

ASCII_LETTERS = list('abcdefghijklmnopqrstuvwxyz') + ['enter', 'tab']
SCREENSHOT_TIME = 5  # second
API_URL = 'http://localhost:4000/api/v1/ocr'


def get_pressed_key(cnt: int) -> Tuple[str, int]:
    for letter in ASCII_LETTERS:
        if keyboard.is_pressed(letter):
            return letter, cnt + 1
    return '', cnt + 1


async def get_praise_text(last_pressed_time: float):

    if time.time() - last_pressed_time <= SCREENSHOT_TIME:
        return ''

    loop = asyncio.get_event_loop()

    screen_shot = await loop.run_in_executor(None, pyautogui.screenshot)
    buffered = BytesIO()
    screen_shot.save(buffered, format='jpg')
    image_str = base64.b64encode(buffered.getvalue()).decode()
    request_json = {'data': image_str}
    response = await loop.run_in_executor(None,
                                          requests.post,
                                          API_URL,
                                          data=request_json)
    return response.text


async def send_json(websocket, key: str, response: str):
    response = json.loads(response)

    ret = {
        'key': key,
        'praise': {
            'isPraise': response != '',
            'text': response
        }
    }
    await websocket.send(json.dumps(ret).encode())


async def sender(websocket, path):

    prev_cnt: int = 0
    cnt: int = 0
    pressed_key: str = ''
    last_pressed_time: float = time.time()

    while True:

        pressed_key, cnt = get_pressed_key(cnt)

        if prev_cnt != cnt:
            last_pressed_time = time.time()

        api_response = await get_praise_text(last_pressed_time)

        await send_json(websocket, pressed_key, api_response)
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    start_server = websockets.serve(sender, "localhost", 18080)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()