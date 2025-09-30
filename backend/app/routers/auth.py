from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST

from backend.app.database import models, schemas
from backend.app.database.db import get_db
from backend.app.security import get_password_hash, create_email_token, SECRET_KEY, ALGORITHM
from backend.app.utils.mailer import send_verification_email

auth_router = APIRouter()

@auth_router.post("/register", response_model=schemas.Player)
def register_user(user: schemas.PlayerCreate, db: Session = Depends(get_db)):
    # Проверяем, есть ли уже такой email или username
    if db.query(models.Player).filter(models.Player.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.Player).filter(models.Player.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Создаём пользователя
    hashed_password = get_password_hash(user.password)
    new_user = models.Player(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Генерируем токен для подтверждения
    token = create_email_token({"sub": new_user.email})
    send_verification_email(new_user.email, token)

    return new_user

@auth_router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = db.query(models.Player).filter(models.Player.email == email).first()
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()
    db.refresh(user)

    return {"message": "Email successfuly verified"}