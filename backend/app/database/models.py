from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    level = Column(Integer, default=1)
    habits = Column(JSON, default=list)
    goals = Column(JSON, default=list)
    preferences = Column(JSON, default=dict)
    experience = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(UTC))
    ai_settings = Column(JSON, default={"enabled": True, "model": "Qwen2.5-7B-Instruct"})

    quests = relationship("GeneratedQuest", back_populates="user")
    tasks = relationship("Task", back_populates="user")

    def add_experience(self, points: int):
        self.experience += points
        self.check_level_up()

    def check_level_up(self):
        exp_needed = self.level ** 2 * 100
        while self.experience >= exp_needed:
            self.experience -= exp_needed
            self.level += 1
            exp_needed = self.level ** 2 * 100


class GeneratedQuest(Base):
    __tablename__ = "generated_quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    steps = Column(JSON, default=list)
    estimated_time = Column(String)
    difficulty = Column(String)
    category = Column(String)
    ai_generated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    ai_model = Column(String, nullable=True)
    generation_prompt = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("players.id"))
    user = relationship("Player", back_populates="quests")

    tasks = relationship("Task", back_populates="quest")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    points = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    completed_at = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey("players.id"))
    user = relationship("Player", back_populates="tasks")

    quest_id = Column(Integer, ForeignKey("generated_quests.id"), nullable=True)
    quest = relationship("GeneratedQuest", back_populates="tasks")
