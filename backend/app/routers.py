import json
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
from main import app
from database import schemas, models
from database.db import get_db
from services.ai_integration import AIservice
from sqlalchemy.orm import Session
from security import get_current_user, get_current_active_user


ai_service = AIservice()

@app.post("/users/me/generate-quest", response_model=schemas.GeneratedQuest)
async def generate_ai_quest(quest_request: schemas.QuestGenerationRequest, current_user: models.Player = Depends(get_current_user),
                            db: Session = get_db()):
    """Генерация персонализированного квеста с помощью AI"""

    # Подготовка данных пользователя
    user_data = {
        "level": current_user.level,
        "goals": current_user.goals or [],
        "habits": current_user.habits or [],
        "preferences": current_user.preferences or {},
        "theme": quest_request.theme,
        "category": quest_request.category
    }

    # Генерация квеста через AI сервис
    ai_response = await ai_service.generate_quest(user_data)

    # Сохранение в базу данных
    db_quest = models.GeneratedQuest(
        title=ai_response["title"],
        description=ai_response["description"],
        steps=ai_response["steps"],
        estimated_time=ai_response["estimated_time"],
        difficulty=ai_response["difficulty"],
        category=ai_response["category"],
        ai_generated=True,
        ai_model=ai_service.default_model,
        user_id=current_user.id
    )

    db.add(db_quest)
    db.commit()

    # Создание задач из шагов квеста
    for step in ai_response["steps"]:
        db_task = models.Task(
            title=step["title"],
            description=step["description"],
            points=step["points"],
            user_id=current_user.id,
            quest_id=db_quest.id
        )
        db.add(db_task)

    db.commit()
    return db_quest

@app.post("/users/me/generate-quest-stream")
async def generate_ai_quest_stream(quest_stream: schemas.QuestGenerationRequest,
                                   current_user: models.Player = Depends(get_current_active_user)):
    """Стриминговая генерация текста (Server-Sent Events)"""

    user_data = {
        "level": current_user.level,
        "goals": current_user.goals or [],
        "habits": current_user.habits or [],
        "preferences": current_user.preferences or {},
    }

    async def generate():
        full_response = ""
        async for chunk in ai_service.generated_quest(user_data, stream=True):
            full_response += chunk
            yield f"data: {json.dumps({'chunk': chunk, 'is_complete': True, 'full_response': full_response})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",  # ← Server-Sent Events
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
@app.get("/users/me/ai-settings", response_model=schemas.AISettings)
def get_ai_settings(current_user: models.Player = Depends(get_current_active_user)):
    """Получение настроек AI пользователя"""

    return current_user.ai_settings or {"enable": True, "model": "Qwen2.5-7B-Instruct"}

@app.put("/users/me/ai-settings", response_model=schemas.AISettings)
def update_ai_settings(settings: schemas.AISettings,
    current_user: models.Player = Depends(get_current_active_user),
    db: Session = Depends(get_db)):
    """Обновление настроек AI"""

    current_user.ai_settings = settings.dict()
    db.commit()
    db.refresh(current_user)
    return current_user.ai_settings