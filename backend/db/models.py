import time

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class GameRecord(Base):
    __tablename__ = "game_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_code = Column(String, nullable=False, index=True)
    scenario_id = Column(String, nullable=False)
    total_players = Column(Integer, nullable=False)
    started_at = Column(Float, nullable=True)
    ended_at = Column(Float, nullable=True)
    winner_faction = Column(String, nullable=True)


class PlayerRecord(Base):
    __tablename__ = "player_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("game_record.id"), nullable=False)
    player_id = Column(String, nullable=False)
    seat_id = Column(Integer, nullable=False)
    role_id = Column(String, nullable=False)
    is_ai = Column(Boolean, default=True)
    provider_name = Column(String, nullable=True)
    personality = Column(String, nullable=True)
    alive_until_round = Column(Integer, nullable=True)


class RoundLog(Base):
    __tablename__ = "round_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("game_record.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    phase = Column(String, nullable=False)
    summary_public = Column(Text, nullable=True)
    timestamp = Column(Float, default=time.time)


class SpeechLog(Base):
    __tablename__ = "speech_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("game_record.id"), nullable=False)
    round_id = Column(Integer, nullable=True)
    player_id = Column(String, nullable=False)
    think_reasoning = Column(Text, nullable=True)
    think_intent = Column(Text, nullable=True)
    will_speak = Column(Boolean, default=False)
    spoken_text = Column(Text, nullable=True)
    timestamp = Column(Float, default=time.time)


class ActionLog(Base):
    __tablename__ = "action_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("game_record.id"), nullable=False)
    round_id = Column(Integer, nullable=True)
    player_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    target_id = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    timestamp = Column(Float, default=time.time)
