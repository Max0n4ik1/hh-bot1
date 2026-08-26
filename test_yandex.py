import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
headers = {
    'Authorization': f'Api-Key {os.getenv("YANDEX_API_KEY")}',
    'Content-Type': 'application/json'
}
data = {
    'modelUri': f'gpt://{os.getenv("YANDEX_FOLDER_ID")}/yandexgpt-lite',
    'completionOptions': {
        'stream': False,
        'temperature': 0.1,
        'maxTokens': 100
    },
    'messages': [
        {'role': 'user', 'text': 'Привет, как дела?'}
    ]
}

print("📤 Отправка запроса...")
response = requests.post(url, headers=headers, json=data)
print(f"📊 Статус: {response.status_code}")
print(f"📄 Ответ: {response.text}")