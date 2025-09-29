from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database.db import init_db
from backend.app.routers.ai_routers import ai_router
from backend.app.routers.auth import  auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print(" Initializing database...")
        init_db()
        print(" Database initialized successfully")
    except Exception as e:
        print(f" Database initialization failed: {e}")
        print("  Continuing without database initialization...")

    yield

    # Shutdown
    print("🔴 Shutting down...")



app = FastAPI(
    title="Life Game App",
    description="RPG-игра для саморазвития с интеграцией AI",
    version="0.1.0",
    lifespan=lifespan
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# --- Root ---
@app.get("/")
def read_root():
    return {"message": "Welcome to Life Game App!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
