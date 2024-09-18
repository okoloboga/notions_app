import requests
import logging
import json

from passlib.context import CryptContext


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')

URL = "http://127.0.0.1:8000"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Регистрация нового пользователя
async def new_user(username: str,
                   password: str):

    hashed_password = pwd_context.hash(password)
    params = {
        "username": username,
        "password": hashed_password
    }
    response = requests.post(f'{URL}/users', json=json.dumps(params), timeout=1).json()
    answer = response.get("replies")

    logger.info(f'result registration: {answer}')

    return answer


# Аутентификация
async def login(username: str,
                password: str):

    hashed_password = pwd_context.hash(password)
    params = {
        "username": username,
        "password": hashed_password
    }
    response = requests.post(f'{URL}/token',
                             json=json.dumps(params), 
                             timeout=1).json()
    answer = response.get("replies")

    logger.info(f'result token: {answer}')

    return answer


# Создание новой записи
async def create_note(data: dict,
                      headers: dict):
    response = requests.post(f'{URL}/notes',
                             json=data,
                             headers=headers,
                             timeout=1).json()
    answer = response.get("replies")

    logger.info(f'result create_note {answer}')

    return answer


# Получение записей
async def notes(headers: dict):
    response = requests.get(f'{URL}/notes', 
                            headers=headers, 
                            timeout=1).json()
    return response


# Поиск записей по тэгу
async def notes_tag(tag: str,
                    headers: dict):
    response = requests.get(f'{URL}/notes/tags/{tag}',  
                            headers=headers,   
                            timeout=1).json()
    return response


