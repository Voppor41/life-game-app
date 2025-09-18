import os
import logging
from typing import Dict, Any, Optional, AsyncGenerator

from httpx import stream
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIservice:

    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.default_model = "Qwen/Qwen2.5-7B-Instruct"

        if not self.api_key:
            logger.warning("HUGGINGFACEHUB_API_TOKEN not found. Some AI features may be disabled.")
            self.client = None
        else:
            self.client = InferenceClient(api_key=self.api_key)

    async def generated_quest(self, user_data: Dict[str, Any], stream: bool = False
                              ) -> AsyncGenerator[str, None] | Dict[str, Any]:

        if not self.client:
            return self._generate_fallback_quest(user_data)

        promt = self._built_quest_promt(user_data)

        try:
            if stream:
                return self._generate_streaming(promt, user_data)
            else:
                return await self._generate_complete(promt, user_data)
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return self.generate_fallback_quest(user_data)

    def _built_quest_promt(self, user_data: Dict[str, Any]) -> str:
        return f"""
        Ты — наставник в RPG-игре о саморазвитии. создай персональный квест для игрока на основе его данных:
        Уровень: {user_data.get('level', 1)}
        Цели: {', '.join(user_data.get('goals', []))}
        Привычки: {', '.join(user_data.get('habits', []))}
        Предпочтения: {user_data.get('preferences', {})}
        
        Создай квест который:
        1. Соответствует целям пользователя
        2. Учитывает его привычки и уровень
        3. Состоит из 3-5 конкретных шагов (задач)
        4. Имеет увлекательное описание и название
        5. Указывает примерное время выполнения
        6. Имеет соответствующую сложность (easy, medium, hard)
        7. Относится к одной из категорий: здоровье, обучение, продуктивность, творчество, спорт
        
        Верни ответ ТОЛЬКО в формате JSON:
        {{
            "title": "Название квеста",
            "description": "Описание квеста",
            "steps": [
                {{
                    "title": "Конкретное название задачи",
                    "description": "Детальное описание что нужно сделать", 
                    "points": 10,
                    "estimated_time": "15 минут"
                }}
            ],
            "estimated_time": "Общее время выполнения",
            "difficulty": "easy/medium/hard",
            "category": "категория"
    }}"""

    async def _generate_complete(self, prompt, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Полная генерация ответа"""

        response = self.client.chat.completions.create(
            model=self.default_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9
        )

        content = response.choices[0].message.content
        return self._parse_ai_response(content, user_data)

    async def _generate_streaming(self, prompt: str, user_data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Стриминговая генерация"""

        stream = self.client.chat.completions.create(
            model=self.default_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            stream=True
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta_content:
                yield chunk.choices[0].delta_content

    def _genrate_fallback_quest(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Резервная генерация квеста (если AI недоступен"""

        goals = user_data.get('goals', [])

        # Простая логика на основе целей пользователя
        if any('здор' in goal.lower() for goal in goals):
            return {
                "title": "Путь к здоровому образу жизни",
                "description": "7-дневный челлендж для улучшения здоровья",
                "steps": [
                    {
                        "title": "Утренняя зарядка 15 минут",
                        "description": "Выполни комплекс утренних упражнений",
                        "points": 25,
                        "estimated_time": "15 минут"
                    }
                ],
                "estimated_time": "7 дней",
                "difficulty": "medium",
                "category": "health"
            }

        return {
            "title": "Базовый квест продуктивности",
            "description": "Начни свой путь к эффективности",
            "steps": [
                {
                    "title": "Планирование дня",
                    "description": "Составь план на день",
                    "points": 30,
                    "estimated_time": "15 минут"
                }
            ],
            "estimated_time": "1 день",
            "difficulty": "easy",
            "category": "productivity"
        }

