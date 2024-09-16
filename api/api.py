import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from models import Note
from schemas import Note as NoteSchema
from schemas import NoteCreate, UserCreate, User
from database import SessionLocal
from auth import (get_current_user, get_user, create_user, 
                  create_access_token, verify_password)

app = FastAPI()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


limiter = Limiter(key_func=get_current_user)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@app.post("/users/", response_model=User)
@limiter.limit("5/seconds")
async def register_user(user: UserCreate,
                        db: AsyncSession = Depends(get_db)):

    logger.info(f'Logging user: {user}')

    existing_user = await get_user(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await create_user(db, user)


@app.post("/token")
@limiter.limit("5/seconds")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):

    logger.info(f'Create token for user: {form_data.username}')

    user = await get_user(db, username=form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/notes/", response_model=List[NoteSchema])
@limiter.limit("5/seconds")
async def read_notes(skip: int = 0,
                     limit: int = 10,
                     db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):

    result = await db.execute(select(Note)
                              .where(Note.owner_id == current_user.id)
                              .offset(skip)
                              .limit(limit))
    notes = result.scalars().all()

    logger.info(f'User {current_user} getting all notes {notes}')

    return notes


@app.post("/notes/", response_model=NoteSchema)
@limiter.limit("5/seconds")
async def create_note(note: NoteCreate,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):

    logger.info(f'User {current_user.username} create new note: {note.dict()}')

    db_note = Note(title=note.title,
                   content=note.content,
                   tags=note.tags,
                   owner_id=current_user.id)

    logger.info(f'{db_note}')

    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note


@app.get("/notes/{note_id}", response_model=NoteSchema)
@limiter.limit("5/seconds")
async def read_note(note_id: int,
                    db: AsyncSession = Depends(get_db)):

    logger.info(f'Getting note with id {note_id}')

    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/notes/{note_id}", response_model=NoteSchema)
@limiter.limit("5/seconds")
async def update_note(note_id: int,
                      note: NoteCreate,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):

    logger.info(f'User {current_user} edit note {note_id}: {note}')

    db_note = await db.get(Note, note_id)
    if not db_note or db_note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")

    for key, value in note.dict().items():
        setattr(db_note, key, value)
    db_note.tags = note.tags
    await db.commit()
    await db.refresh(db_note)
    return db_note


@app.delete("/notes/{note_id}", response_model=NoteSchema)
@limiter.limit("5/seconds")
async def delete_note(note_id: int, db:
                      AsyncSession = Depends(get_db)):
    db_note = await db.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    await db.delete(db_note)
    await db.commit()
    return db_note


@app.get("/notes/tags/{tag_name}", response_model=List[NoteSchema])
@limiter.limit("5/seconds")
async def read_notes_by_tag(tag_name: str, db:
                            AsyncSession = Depends(get_db)):

    logger.info(f'Getting notes by tag: {tag_name}')

    result = await db.execute(select(Note)
                              .where(Note.tags.contains(tag_name)))
    notes = result.unique().scalars().all()
    return notes

