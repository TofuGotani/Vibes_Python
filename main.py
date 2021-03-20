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
import functools

ASCII_LETTERS = list('abcdefghijklmnopqrstuvwxyz') + ['enter', 'tab', 'space']
SCREENSHOT_TIME = 5  # second
# API_URL = 'http://localhost:4000/api/v1/ocr'
API_URL = 'https://tofugotani-vibes.herokuapp.com/api/v1/ocr'  # 本番環境
WAIT_API_TIME = 30


def get_pressed_key(cnt: int) -> Tuple[str, int]:
    for letter in ASCII_LETTERS:
        if keyboard.is_pressed(letter):
            return letter, cnt + 1
    return '', cnt


async def get_praise_text() -> str:
    print('take screen shot')
    loop = asyncio.get_event_loop()

    screen_shot = await loop.run_in_executor(None, pyautogui.screenshot)
    buffered = BytesIO()
    screen_shot = screen_shot.convert('RGB')
    screen_shot.save(buffered, format='JPEG')
    image_str = base64.b64encode(buffered.getvalue()).decode()
    request_json = {'data': image_str}

    func = functools.partial(requests.post, API_URL, data=request_json)
    try:
        response = await loop.run_in_executor(None, func)
        print(f"status code is {response.status_code}")
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            return ''
    except:
        pass


async def send_json(websocket, key: str, response: str):
    if response != '':
        response = json.loads(response)
    message = response['message'] if 'message' in response else ''
    print(response)
    if(key == ''):
        ret = {'key': key, 'praise': {'isPraise': message['text'] != '','praiseData': {'text': message['text'],'cats': message['cats']}}}
    else:
        ret = {'key': key, 'praise': {'isPraise': False,'praiseData': {'text':'','cats':0}}}


    print(json.dumps(ret).encode())

    await websocket.send(json.dumps(ret).encode())


async def sender(websocket, path):

    prev_cnt: int = 0
    cnt: int = 0
    pressed_key: str = ''
    last_pressed_time: float = time.time()
    is_took_screenshot: bool = False
    api_response: str = ''

    while True:
        api_response: str = ''
        pressed_key, cnt = get_pressed_key(cnt)

        # キーが入力されたかどうか
        if prev_cnt != cnt:
            await send_json(websocket, pressed_key, api_response)
            is_took_screenshot = False
            last_pressed_time = time.time()

        # 一定時間たったかどうか
        if time.time(
        ) - last_pressed_time > SCREENSHOT_TIME and not is_took_screenshot:
            api_response = await get_praise_text()
            if api_response != '':
                await send_json(websocket, pressed_key, api_response)
                is_took_screenshot = True
            else:
                last_pressed_time = time.time() + WAIT_API_TIME

        prev_cnt = cnt

        await asyncio.sleep(0.1)


if __name__ == '__main__':
    print('start server')
    start_server = websockets.serve(sender, "localhost", 18080)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
