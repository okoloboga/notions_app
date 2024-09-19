from pydantic import BaseModel
from typing import List
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class Token(BaseModel):
    password: str


class User(UserBase):
    id: int
    notes: List["Note"] = []

    class Config:
        orm_mode = True


class NoteBase(BaseModel):
    title: str
    content: str
    tags: str


class NoteCreate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        orm_mode = True

