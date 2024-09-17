import logging

from aiogram import Router
from aiogram.flters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from redis import asyncio as aioredis

from fluentogram import TranslatorRunner
from states import MainSG
from requests import *


router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')

r = aioredis.Redis(host='localhost', port=6379)


# Обработка команды START
@router.message(CommandStart())
async def command_start_getter(message: Message,
                               dialog_manager: DialogManager):

    username = message.from_user.username

    logger.info(f'User {username} start Bot')

    # Проверка сущесвования пользователя в БД
    exists = await new_user(username=username,
                            password='')
    logger.info(f'Is user {username} exists?')

    if exists:
        await dialog_manager.start(MainSG.login())
    else:
        await dialog_manager.start(MainSG.registration())


# Проверка и возвращение результата регистрации
async def registration_result(message: Message,
                              widget: ManagedTextInput,
                              dialog_manager: DialogManager,
                              password: str):

    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')

    logger.info(f'User {username} in registration process')

    result = await new_user(username, password)
    
    logger.info(f'Registration result: {result}')

    if result:
        await message.answer(text=i18n.registration.complete())
        await dialog_manager.switch_to(MainSG.login())
    else:
        await message.answer(text=i18n.already.registred())
        await dialog_manager.switch_to(MainSG.login())


# Проверка и возвращение результата аутентификации
async def login_result(message: Message,
                       widget: ManagedTextInput,
                       dialog_manager: DialogManager,
                       password: str):

    user_id = message.from_user.id
    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')

    logger.info(f'User {username} in login process')

    result = await login(username, password, user_id)

    logger.info(f'Users login result is {result}')

    if result:
        await r.set(user_id, result['token'], ex=1800)
        await dialog_manager.switch_to(MainSG.main())
    else:
        await message.answer(text=i18n.wrong.password())


# Обработка команды create_note
async def create_note(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):
    
    username = callback.from_user.username
    logger.info(f'User {username} entered create_note')
    await dialog_manager.switch_to(MainSG.create())


# Обработка команды my_notes
async def my_notes(callback: CallbackQuery,
                   button: Button,
                   dialog_manager: DialogManager):

    user_id = callback.from_user.id
    username = callback.from_user.username
    logger.info(f'User {username} get notes list')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')    

    # Получение JWT из Redis по user_id
    if await r.exists(user_id) != 0:
        token = r.get(user_id)

        try:
            headers = {"Authorization": f"Bearer {token}"}
            result = await notes(headers)

            if result.status_code == 200:
                logger.info(f'Getting my_notes by {username} result code: 200')
                await callback.message.answer(text=result.json())
            elif response.status_code == 401:
                logger.info(f'Getting my_notes by {username} result code: 401')
                await callback.message.answer(text=i18n.invalid.token())
                await r.delete(user_id)
                await dialog_manager.switch_to(MainSG.login())
            else:
                logger.info(f'Getting my_notes by {username} result code: {response.status_code}')
                await callback.message.answer(text=i18n.error())

        except request.exceptions.RequestException as e:
            await callback.message.asnwer(text=i18n.server.error())
    else:
        await callback.message.answer(text=i18n.auth.error())
        await dialog_manager.switch_to(MainSG.login())


# Обработка команды tag_notes_list
async def tags_notes_list(message: Message,
                          widget: ManagedTextInput,
                          dialog_manager: DialogManager,
                          tag: str):

    user_id = callback.from_user.id
    username = callback.from_user.username
    logger.info(f'User {username} get notes list by tag')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')    

    # Получение JWT из Redis по user_id
    if await r.exists(user_id) != 0:
        token = r.get(user_id)

        try:
            headers = {"Authorization": f"Bearer {token}"}
            result = await notes_tag(tag, headers)

            if result.status_code == 200:
                logger.info(f'Getting my_notes by {username} result code: 200')
                await callback.message.answer(text=result.json())
            elif response.status_code == 401:
                logger.info(f'Getting my_notes by {username} result code: 401')
                await callback.message.answer(text=i18n.invalid.token())
                await r.delete(user_id)
                await dialog_manager.switch_to(MainSG.login())
            else:
                logger.info(f'Getting my_notes by {username} result code: {response.status_code}')
                await callback.message.answer(text=i18n.error())

        except request.exceptions.RequestException as e:
            await callback.message.asnwer(text=i18n.server.error())
    else:
        await callback.message.answer(text=i18n.auth.error())
        await dialog_manager.switch_to(MainSG.login())