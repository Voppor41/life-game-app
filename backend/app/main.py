from fastapi import FastAPI
from .services.ai_integration import generate_daily_quest

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "Ok"}


