from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from security import get_password_hash, verify_password
import json

Base = declarative_base()

class Player(Base):

    __tablename__ = "Player"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    level = Column(Integer, default=1)
    habits = Column(JSON, default=[])
    goals = Column(JSON, default=[])
    preferences = Column(JSON, default={})
    experience = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    quests = relationship("Quests", back_populates="player")
    generated_quests = relationship("GeneratedQuest", back_populates="user")

    def set_password(self, password: str):
        self.hashed_password = get_password_hash(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)

    def add_experience(self, points: int):
        self.experience += points
        self.check_level_up()

    def check_level_up(self):

        exp_needed = self.level ** 2 * 100
        while self.experience >= exp_needed:
            self.experience -= exp_needed
            self.level += 1
            exp_needed = self.level ** 2 * 100

    def add_goal(self, goal: str):
        goals = self.goals
        if goal not in goals:
            goals.append(goal)
            self.goals = goals

    def add_habbits(self, habit: str):
        habits = self.habits
        if habit not in habits or []:
            habits.append(habit)
            self.habits = habits


class GeneratedQuest(Base):
    __tablename__ = "generated_quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    steps = Column(JSON, default=[])  # Шаги для выполнения квеста
    estimated_time = Column(String)  # Примерное время выполнения
    difficulty = Column(String)  # easy, medium, hard
    category = Column(String)  # health, learning, productivity, etc.
    ai_generated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="generated_quests")

    # Связь с задачами
    tasks = relationship("Task", back_populates="quest")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    points = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tasks")

    # Связь с квестом
    quest_id = Column(Integer, ForeignKey("generated_quests.id"), nullable=True)
    quest = relationship("GeneratedQuest", back_populates="tasks")
