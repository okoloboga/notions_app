import logging

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from models import Note
from schemas import Note as NoteSchema
from schemas import NoteCreate, UserCreate, User, Token
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
    logger.info(f'get_db')
    async with SessionLocal() as session:
        yield session


@app.post("/users/", response_model=User)
@limiter.limit("5/second")
async def register_user(request: Request,
                        user: UserCreate,
                        db: AsyncSession = Depends(get_db)):
    """
    Registers a new user.

    Args:
        request (Request): The incoming request object.
        user (UserCreate): The user data to be registered.
        db (AsyncSession): The asynchronous database session. Defaults to Depends(get_db).

    Returns:
        User
    """
    logger.info(f'Logging user: {user.username}')

    existing_user = await get_user(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await create_user(db, user)


@app.post("/token/", response_model=Token)
@limiter.limit("5/second")
async def login(request: Request,
                form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    """
    Generates a token for the given user.

    Args:
        request (Request): The incoming request object.
        form_data (OAuth2PasswordRequestForm): The form data from the request.
        db (AsyncSession): The asynchronous database session. Defaults to Depends(get_db).

    Returns:
        Token: The generated token.
    """
    logger.info(f'Create token for user: {form_data.username}')

    user = await get_user(db, username=form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"password": create_access_token(data={"sub": user.username})}


@app.get("/notes/", response_model=List[NoteSchema])
@limiter.limit("5/second")
async def read_notes(request: Request,
                     skip: int = 0,
                     limit: int = 10,
                     db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    """
    Get all notes for the current user.

    Args:
        request (Request): The incoming request object.
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The number of records to return. Defaults to 10.
        db (AsyncSession): The asynchronous database session. Defaults to Depends(get_db).
        current_user (User): The current user. Defaults to Depends(get_current_user).

    Returns:
        List[NoteSchema]: The list of notes for the current user.
    """
    result = await db.execute(select(Note)
                              .where(Note.owner_id == current_user.id)
                              .offset(skip)
                              .limit(limit))
    notes = result.unique().scalars().all()

    logger.info(f'User {current_user} getting all notes {notes}')

    return notes


@app.post("/notes/", response_model=NoteSchema)
@limiter.limit("5/second")
async def create_note(request: Request,
                      note: NoteCreate,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)
                      ):
    """
    Create a new note for the current user.

    Args:
        request (Request): The incoming request object.
        note (NoteCreate): The note data to be created.
        db (AsyncSession): The asynchronous database session. Defaults to Depends(get_db).
        current_user (User): The current user. Defaults to Depends(get_current_user).

    Returns:
        NoteSchema: The created note.
    """
    logger.info(f'User {current_user.username} create new note: {note.dict()}')

    # Create a new note
    db_note = Note(title=note.title,
                   content=note.content,
                   tags=note.tags,
                   owner_id=current_user.id)

    logger.info(f'Creating note: {db_note}')
    logger.info(f'{db_note}')

    # Add the note to the database
    db.add(db_note)
    await db.commit()

    # Refresh the database entry
    await db.refresh(db_note)

    # Return the created note
    return db_note


@app.get("/notes/{note_id}", response_model=NoteSchema)
@limiter.limit("5/second")
async def read_note(request: Request,
                    note_id: int,
                    db: AsyncSession = Depends(get_db)):
    """
    Get a note by its ID.

    Args:
        request (Request): The incoming request object.
        note_id (int): The ID of the note to retrieve.
        db (AsyncSession): The asynchronous database session. Defaults to Depends(get_db).

    Returns:
        NoteSchema: The retrieved note.
    """
    logger.info(f'Getting note with id {note_id}')

    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    logger.info(f'Note with id {note_id} found: {note}')

    return note


@app.put("/notes/{note_id}", response_model=NoteSchema)
@limiter.limit("5/second")
async def update_note(request: Request,
                      note_id: int,
                      note: NoteCreate,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    """
    Update a note.

    Args:
        request (Request): The incoming request object.
        note_id (int): The ID of the note to update.
        note (NoteCreate): The note data to update.
        db (AsyncSession): The asynchronous database session. Defaults to Depends(get_db).
        current_user (User): The current user. Defaults to Depends(get_current_user).

    Returns:
        NoteSchema: The updated note.
    """
    logger.info(f'User {current_user} edit note {note_id}: {note}')

    db_note = await db.get(Note, note_id)
    if not db_note or db_note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update the note
    for key, value in note.dict().items():
        setattr(db_note, key, value)
    db_note.tags = note.tags
    await db.commit()
    await db.refresh(db_note)
    return db_note


@app.delete("/notes/{note_id}", response_model=NoteSchema)
@limiter.limit("5/second")
async def delete_note(request: Request,
                      note_id: int, db:
                      AsyncSession = Depends(get_db)):
    """
    Delete a note.

    Args:
        request (Request): The incoming request object.
        note_id (int): The ID of the note to delete.
        db (AsyncSession): The asynchronous database session. Defaults to Depends(get_db).

    Returns:
        NoteSchema: The deleted note.
    """
    logger.info(f'Deleting note {note_id}')

    db_note = await db.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    await db.delete(db_note)
    await db.commit()
    return db_note


@app.get("/notes/tags/{tag_name}", response_model=List[NoteSchema])
@limiter.limit("5/second")
async def read_notes_by_tag(request: Request,
                            tag_name: str, db:
                            AsyncSession = Depends(get_db)):
    """
    Get all notes containing the specified tag.

    Args:
        request (Request): The incoming request object.
        tag_name (str): The tag to search for.
        db (AsyncSession): The asynchronous database session. Defaults to Depends(get_db).

    Returns:
        List[NoteSchema]: The list of notes containing the specified tag.
    """
    logger.info(f'Getting notes by tag: {tag_name}')

    # Search for notes containing the specified tag
    result = await db.execute(select(Note)
                              .where(Note.tags.contains(tag_name)))
    notes = result.unique().scalars().all()
    return notes

