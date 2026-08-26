import os
import requests
from dotenv import load_dotenv

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")


def ask_yandex_gpt(prompt: str, context: str = None) -> str:
    """
    Отправляет запрос к YandexGPT через REST API.
    """
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    
    if context:
        system_prompt = f"""
        Ты — ассистент-эксперт по API HeadHunter (HH.ru).
        Отвечай на вопросы, используя ТОЛЬКО этот контекст.
        Если в контексте нет ответа, скажи, что не знаешь.
        Отвечай на русском языке, четко и по делу.
        
        Контекст:
        {context}
        """
        messages.append({
            "role": "system",
            "text": system_prompt.strip()
        })
    
    messages.append({
        "role": "user",
        "text": prompt
    })
    
    data = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,
            "maxTokens": 2000
        },
        "messages": messages
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        answer = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
        
        if not answer:
            return "Не удалось получить ответ от модели."
            
        return answer.strip()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при запросе к YandexGPT: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"📄 Полный ответ сервера: {e.response.text}")
        return "Извините, произошла ошибка при обработке запроса."