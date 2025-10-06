from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.database.db import get_db
from backend.app.database import models
from backend.app.security import verify_password, create_access_token, create_refresh_token

lg_router = APIRouter()

@lg_router.post("/login")
def login(form_data:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = (
        db.query(models.Player)
        .filter(
            (models.Player.username == form_data.username)
            | (models.Player.email == form_data.username)
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(form_data.password, user.hashed_password):
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

@lg_router.post("/token")
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):

    user = (
        db.query(models.Player)
        .filter(
            (models.Player.username == form_data.username)
            | (models.Player.email == form_data.username)
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}