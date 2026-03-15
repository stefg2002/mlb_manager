# TODO: Add database models for Users and Team Post tables
from __future__ import annotations

from datetime import datetime

from typing import List

from sqlalchemy import ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    google_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(25), nullable=False)

class GoogleUser(Base):
    __tablename__ = "google_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) 

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now())

# class Team(Base):
#     __tablename__ = "team"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     team_name: Mapped[str] = mapped_column(String(100), nullable=False)
#     post_name: Mapped[str] = mapped_column(String(200), nullable=False)
#     players: Mapped[List[Player]] = relationship(back_populates="team")
#     author: Mapped[User] = relationship(back_populates="posts")

# class Player(Base):
#     __tablename__ = "players"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     first_name: Mapped[str] = mapped_column(String(50), nullable=False)
#     last_name: Mapped[str] = mapped_column(String(50), nullable=False)
#     age: Mapped[int] = mapped_column(Integer)
#     position: Mapped[str] = mapped_column(String(2), nullable=False)
#     bats: Mapped[str] = mapped_column(String(1), nullable=False)
#     throws: Mapped[str] = mapped_column(String(1), nullable=False)
#     contract: Mapped[Contract] = relationship(back_populates="player", cascade="all, delete-orphan") # Will relate to contract model
#     service_time: Mapped[int] = mapped_column(Integer)

# class Contract(Base):
#     __tablename__ = "contracts"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
#     player: Mapped[Player] = relationship(back_populates="contract")
#     year_signed: Mapped[int] = mapped_column(Integer)
#     year_end: Mapped[int] = mapped_column(Integer)
#     total_years: Mapped[int] = mapped_column(Integer)
#     total_value: Mapped[int] = mapped_column(Integer)
#     aav: Mapped[int] = mapped_column(Integer)   
#     type: Mapped[str] = mapped_column(String(50), nullable=False) #Guaranteed, 1/2/3-Arb, Prearb
