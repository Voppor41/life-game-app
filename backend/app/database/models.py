from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Player(Base):

    __tablename__ = "Player"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    quests = relationship("Quests", back_populates="player")

    def add_level(self, points: int):
        self.experience += points
        self.check_level_up()

    def check_level_up(self):

        exp_needed = self.level ** 2 * 100
        while self.experience >= exp_needed:
            self.experience -= exp_needed
            self.level += 1
            exp_needed = self.level ** 2 * 100

class Quests(Base):

    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    difficult = Column(String)
    point = Column(Integer, default=0)
    is_compleated = Column(Boolean, default=False)
    created_time = Column(DateTime, default=datetime.utcnow)
    compleated_at = Column(DateTime, nullable=False)

    player_id = Column(Integer, ForeignKey("player.id"))

    player = relationship("Player", back_populates="quests")

