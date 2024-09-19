from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import get_config, DbConfig


db_config = get_config(DbConfig, "db")

engine = create_async_engine(url=str(db_config.dsn), 
                             echo=False)

SessionLocal = sessionmaker(autocommit=False, 
                            autoflush=False, 
                            bind=engine, 
                            class_=AsyncSession)

Base = declarative_base()
