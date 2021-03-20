import keyboard
import time
ASCII_LETTERS = list('abcdefghijklmnopqrstuvwxyz')

if __name__ == '__main__':
    prev_cnt = cnt = 0
    key = ""
    print("start")
    while True:
        for c in ASCII_LETTERS:
            if keyboard.is_pressed(c):
                cnt += 1
                key = c

        if prev_cnt != cnt:
            print(key)
        prev_cnt = cnt
        time.sleep(0.1)
