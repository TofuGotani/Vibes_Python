import asyncio
import websockets
import keyboard

ASCII_LETTERS = list('abcdefghijklmnopqrstuvwxyz') + ['enter', 'tab', 'space', 'delete', 'ctrl', 'shift']


async def sender(websocket, path):
    prev_cnt = cnt = 0
    key = ""
    while True:
        for c in ASCII_LETTERS:
            if keyboard.is_pressed(c):
                key = c
                cnt += 1

        if prev_cnt != cnt:
            await websocket.send(key)
            print(key)
        prev_cnt = cnt
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    print("server started")
    start_server = websockets.serve(sender, "localhost", 18080)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
