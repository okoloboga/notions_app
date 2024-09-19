import logging

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import User
from schemas import UserCreate
from database import SessionLocal
from config import get_config, Salt, JWT

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')

SALT = str(get_config(Salt, 'salt'))
SECRET_KEY = str(get_config(JWT, 'jwt'))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


def verify_password(plain_password: str,
                    hashed_password: str) -> bool:
    """
    Verifies a plain password against its hashed version.

    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to compare with.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    logger.info(f'verify_password: {plain_password}, {hashed_password}')

    return pwd_context.verify(plain_password, hashed_password)


def encrypt_password(password: str) -> str:
    """
    Encrypts a plain password using bcrypt.

    Args:
        password (str): The plain password to encrypt.

    Returns:
        str: The hashed password.
    """
    logger.info(f'encrypt_password: {password}')

    hashed_password = pwd_context.hash(password)
    return hashed_password


async def get_user(db: AsyncSession, 
                   username: str) -> Optional[User]:
    """
    Retrieves a user by their username

    Args:
        db (AsyncSession): The database session to use.
        username (str): The username of the user to retrieve.

    Returns:
        Optional[User]: The user if found, None otherwise.
    """
    logger.info(f'get user by username {username}')

    result = await db.execute(select(User).where(User.username == username))  
    return result.scalar()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    Creates a user in the database.

    Args:
        db (AsyncSession): The database session to use.
        user (UserCreate): The user data to create.

    Returns:
        User: The newly created user.
    """
    logger.info(f'create user with username: {user.username}')

    db_user = User(username=user.username, 
                   password=encrypt_password(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


def create_access_token(data: dict, 
                        expires_delta: Optional[timedelta] = None):
    """
    Creates an access token based on the given data.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[timedelta], optional): 
            The time delta after which the token will expire. 
            Defaults to 15 minutes.

    Returns:
        str: The created access token.
    """
    logger.info(f'creating token {data}')

    # Create a copy of the data to encode
    to_encode = data.copy()

    # Set the expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    # Update the data with the expiration time
    to_encode.update({"exp": expire})

    logger.info(f'to_encode: {to_encode}')

    # Encode the data using the JWT algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    logger.info(f'created token: {encoded_jwt}')

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), 
                           db: AsyncSession = Depends(get_db)) -> User:
    """
    Retrieves the user based on the given token

    Args:
        token (str): The token to use for authentication.
        db (AsyncSession): The database session to use for the query.

    Returns:
        User: The user associated with the token.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    logger.info(f'getting user by token: {token}')

    # Define the exception to raise if the credentials are invalid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to decode the token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        # If the username is not found, raise the exception
        if username is None:
            raise credentials_exception
    except JWTError:
        # Raise the exception if there is an error decoding the token
        raise credentials_exception

    # Get the user from the database
    user = await get_user(db, username=username)

    logger.info(f'Getted user: {user}')

    # If the user is not found, raise the exception
    if user is None:
        raise credentials_exception

    # Return the user
    return user

