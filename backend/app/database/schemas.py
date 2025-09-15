from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class PlayerBase(BaseModel):
    username: str
    email: EmailStr

class PlayerCreate(BaseModel):
    password: str

class Player(PlayerBase):
    id: int
    level: int
    experience: int
    created_at: datetime

    class Config:
        from_attributes = True

class QuestBase(BaseModel):
    title: str
    description: Optional[str] = None
    points: int

class QuestCreate(QuestBase):
    pass

class Quest(QuestBase):
    id: int
    user_id: int
    is_complited: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuestComplete(BaseModel):
    is_complited: bool = True