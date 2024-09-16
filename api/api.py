from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Note
from schemas import NoteCreate, Note
from database import SessionLocal


app = FastAPI()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@app.post("/users/", response_model=User)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await create_user(db, user)


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/notes/", response_model=List[Note])
async def read_notes(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Note).where(Note.owner_id == current_user.id).offset(skip).limit(limit))
    notes = result.scalars().all()
    return notes


@app.post("/notes/", response_model=Note)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_note = Note(**note.dict(), owner_id=current_user.id)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note


@app.get("/notes/{note_id}", response_model=Note)
async def read_note(note_id: int, db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, note: NoteCreate, db: AsyncSession = Depends(get_db)):
    db_note = await db.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    for key, value in note.dict().items():
        setattr(db_note, key, value)

    await db.commit()
    await db.refresh(db_note)
    return db_note


@app.delete("/notes/{note_id}", response_model=Note)
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    db_note = await db.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    await db.delete(db_note)
    await db.commit()
    return db_note


@app.get("/notes/tags/{tag_name}", response_model=List[Note])
async def read_notes_by_tag(tag_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.tags.contains(tag_name)))
    notes = result.scalars().all()
    return notes

