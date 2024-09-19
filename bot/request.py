import requests
import logging
import json


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')

URL = "http://127.0.0.1:8000"


# Регистрация нового пользователя
async def new_user(username: str,
                   password: str):
    payload = {
        "username": username,
        "password": password
    }

    logger.info(f'new_user {username}')

    response = requests.post(f'{URL}/users/', 
                             json=payload, 
                             timeout=1)

    logger.info(f'result registration: {response.status_code}')

    return response.status_code


# Аутентификация
async def login(username: str,
                password: str):
    payload = {
       "grant_type": "password",
       "username": username,
       "password": password
    }

    logger.info(f'login {username}')

    response = requests.post(f'{URL}/token/',
                             data=payload, 
                             timeout=1)

    logger.info(f'login status code: {response.status_code}')

    return response


# Создание новой записи
async def new_note(data: dict, 
                   headers: dict):
    
    logger.info(f'create_note: {data}')

    response = requests.post(f'{URL}/notes/',
                             json=data,
                             headers=headers,
                             timeout=1)

    logger.info(f'result create_note {response}')

    return response


# Получение записей
async def notes(headers: dict):

    logger.info(f'getting notes headers: {headers}')

    response = requests.get(f'{URL}/notes/', 
                            headers=headers, 
                            timeout=1)

    logger.info(f'getting notes {response}')
    
    return response


# Поиск записей по тэгу
async def notes_tag(tag: str,
                    headers: dict):
    response = requests.get(f'{URL}/notes/tags/{tag}',  
                            headers=headers,   
                            timeout=1)
    
    logger.info(f'tags search {response}')

    return response


