from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.database.db import get_db
from backend.app.database import models
from backend.app.security import verify_password, create_access_token, create_refresh_token

lg_router = APIRouter()

@lg_router.post("/login")
def login(from_data:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.Player).filter(models.Player.username == from_data.username).first

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(from_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Please verify your email before logging")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }