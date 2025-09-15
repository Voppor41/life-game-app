import os
from dotenv import load_dotenv
import requests

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

def generate_daily_quest(user_data: dict) -> dict:
    print(os.getenv("HUGGINGFACE_API_KEY"))

    if not HF_API_KEY:
        return {"error": "HF_API_KEY not found in environment variables"}

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    prompt = f"""
Ты — наставник в RPG-игре о саморазвитии.
Сгенерируй одно задание для пользователя в формате:

🎯 Задание: ...
📜 Описание: ...
🏆 Награда: ...
⏰ Срок: ...

Данные пользователя:
Имя: {user_data['username']}
Уровень: {user_data['level']}
Настроение: {user_data['mood']}
Привычки: {user_data['habits']}
Цели: {user_data['goals']}
"""

    payload = {"inputs": prompt}

    try:
        resp = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        # Ответ от HF иногда массив, иногда строка
        if isinstance(data, list) and "generated_text" in data[0]:
            content = data[0]["generated_text"]
        elif isinstance(data, dict) and "error" in data:
            return {"error": data["error"]}
        else:
            return {"raw": data}

        quest = {}
        for line in content.splitlines():
            if "🎯" in line:
                quest['title'] = line.split(":", 1)[-1].strip()
            elif "📜" in line:
                quest['description'] = line.split(":", 1)[-1].strip()
            elif "🏆" in line:
                quest['reward'] = line.split(":", 1)[-1].strip()
            elif "⏰" in line:
                quest['deadline'] = line.split(":", 1)[-1].strip()

        return quest if quest else {"raw": content}
    except Exception as e:
        return {"error": str(e)}
