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

class PlayerPreferences(BaseModel):
    preferred_categories: List[str]
    time_availability: str = "medium"   # low, medium, high
    difficulty_preference: str = "medium"   # easy, medium, hard

class PlayerUpdate(BaseModel):
    goals: Optional[List[str]] = None
    habits: Optional[List[str]] = None
    preference: Optional[List[str]] = None


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    points: int = 0


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    user_id: int
    is_completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskComplete(BaseModel):
    is_completed: bool = True

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


class QuestStep(BaseModel):
    title: str
    description: str
    points: int
    estimated_time: str


class GeneratedQuestBase(BaseModel):
    title: str
    description: str
    steps: List[QuestStep]
    estimated_time: str
    difficulty: str
    category: str


class GeneratedQuestCreate(GeneratedQuestBase):
    pass


class GeneratedQuest(GeneratedQuestBase):
    id: int
    user_id: int
    ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QuestGenerationRequest(BaseModel):
    theme: Optional[str] = None
    category: Optional[str] = None


class QuestGenerationResponse(BaseModel):
    quest: GeneratedQuest
    tasks: List[Task]