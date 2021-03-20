import pyautogui
import base64
from io import BytesIO
import json
import requests

api_url = 'http://localhost:3000/api/v1/ocr'

screen_shot = pyautogui.screenshot()

# print(type(screen_shot))
# print(screen_shot.size, screen_shot.format)

buffered = BytesIO()
screen_shot.save(buffered, format='png')

# print(screen_shot.size)
img_str = base64.b64encode(buffered.getvalue()).decode()

# print(img_str)
request_json = {'data': base64.b64encode(buffered.getvalue()).decode()}
# request_json = {'data': 'hi'}

# print(request_json)

payload = json.dumps(request_json).encode('UTF-8')

response = requests.post(api_url, data=request_json)

print(response.text)
