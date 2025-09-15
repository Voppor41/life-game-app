import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
DEEPINFRA_API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"  # можно менять на другую

def generate_daily_quest(user_data: dict) -> dict:
    if not DEEPINFRA_API_KEY:
        return {"error": "DEEPINFRA_API_KEY not found in .env"}

    headers = {
        "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Ты — наставник в RPG-игре о саморазвитии.
Сгенерируй одно задание для пользователя в формате:

🎯 Задание: ...
📜 Описание: ...
🏆 Награда: ...
⏰ Срок: ...

Данные пользователя:
Имя: {user_data['name']}
Уровень: {user_data['level']}
Настроение: {user_data['mood']}
Привычки: {user_data['habits']}
Цели: {user_data['goals']}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты — помощник-наставник в RPG об улучшении жизни."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 300
    }

    try:
        resp = requests.post(DEEPINFRA_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        quest = {}
        for line in content.splitlines():
            if "🎯" in line:
                quest['title'] = line.split(":",1)[-1].strip()
            elif "📜" in line:
                quest['description'] = line.split(":",1)[-1].strip()
            elif "🏆" in line:
                quest['reward'] = line.split(":",1)[-1].strip()
            elif "⏰" in line:
                quest['deadline'] = line.split(":",1)[-1].strip()

        return quest if quest else {"raw": content}
    except Exception as e:
        return {"error": str(e)}
