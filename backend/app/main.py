from fastapi import FastAPI
from .services.ai_integration import generate_daily_quest

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "Ok"}

@app.get("/ai/quest")
async def ai_quest():

    user = {
        "username": "Test user",
        "level": 3,
        "mood": "среднее",
        "habits": "часто скроллит соцсети, пропускает утренние рутины",
        "goals": "повысить продуктивность"
    }

    quests = generate_daily_quest(user)
    return quests

