import logging
import requests

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, message
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input.text import ManagedTextInput
from redis import asyncio as aioredis

from fluentogram import TranslatorRunner
from states import MainSG
from request import *


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
        await dialog_manager.start(state=MainSG.login)
    else:
        await dialog_manager.start(state=MainSG.registration)


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
        await dialog_manager.switch_to(state=MainSG.login)
    else:
        await message.answer(text=i18n.already.registred())
        await dialog_manager.switch_to(state=MainSG.login)


# Проверка и возвращение результата аутентификации
async def login_result(message: Message,
                       widget: ManagedTextInput,
                       dialog_manager: DialogManager,
                       password: str):

    user_id = message.from_user.id
    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')

    logger.info(f'User {username} in login process')

    result = await login(username, password)

    logger.info(f'Users login result is {result}')

    if result:
        await r.set(str(user_id), result['token'], ex=1800)
        await dialog_manager.switch_to(state=MainSG.main)
    else:
        await message.answer(text=i18n.wrong.password())


'''Процесс создания записи'''
# Обработка команды create_note
async def create_note(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):
    
    username = callback.from_user.username
    logger.info(f'User {username} entered create_note')
    await dialog_manager.switch_to(state=MainSG.title)


# Обработка ввода заголовка записи
async def check_title(message: Message,
                      widget: ManagedTextInput,
                      dialog_manager: DialogManager,
                      title: str):

    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')
    
    logger.info(f'User {username} create new note with title: {title}')

    if len(title) < 15:
        await state.update_data(title=title)
        await dialog_manager.switch_to(state=MainSG.content)
    else:
        await message.answer(text=i18n.toolong.title())


# Обработка ввода содержания записи
async def check_content(message: Message,
                        widget: ManagedTextInput,
                        dialog_manager: DialogManager,
                        content: str):

    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')   

    logger.info(f'User {username} create new note with content:\n{content}')

    if len(content) < 700:
        await state.update_data(content=content)
        await dialog_manager.switch_to(state=MainSG.tags)
    else:
        await message.answer(text=i18n.toolong.content())


# Обработка ввода тэгов записи
async def check_tags(message: Message,
                     widget: ManagedTextInput,
                     dialog_manager: DialogManager,
                     tags: str):

    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')
    
    logger.info(f'User {username} create new note with tags: {tags}')

    tags_list = ' '.join(tags)
    if len(tags_list) < 6:
        await state.update_data(tags=tags)
        await dialog_manager.switch_to(state=MainSG.complete)
    else:
        await message.answer(text=i18n.toolong.tags())


# Подтверждение создания записи
async def confirm(callback: CallbackQuery,
                  button: Button,
                  dialog_manager: DialogManager):

    user_id = message.from_user.id
    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')
    completed_note = await state.get_data()

    logger.info(f'User {username} complete note: {completed_note}')
    
    # Получение JWT из Redis по user_id
    if await r.exists(user_id) != 0:
        token = r.get(user_id)

        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await create_note(data=completed_note,
                                         headers=headers)
            if response.status_codes == 200:
                logger.info(f'Create note by {username} result code: 200')
                await callback.message.answer(text=i18n.note.created())
            elif response.status_code == 401:
                logger.info(f'Create note by {username} result code: 401')
                await callback.message.answer(text=i18n.invalid.token())
                await r.delete(user_id)
                await dialog_manager.switch_to(state=MainSG.login)
            else:
                logger.info(f'Create note by {username} result code: {response.status_code}')
                await callback.message.answer(text=i18n.error())

        except requests.exceptions.RequestException as e:
            logger.info(f'Create note by {username} error {e}')
            await callback.message.asnwer(text=i18n.server.error())
    else:
        await callback.message.answer(text=i18n.auth.error())
        await dialog_manager.switch_to(state=MainSG.login)


# Отмена создания записи
async def cancel(callback: CallbackQuery,
                 button: Button,
                 dialog_manager: DialogManager):

    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')

    await callback.message.answer(text=i18n.canceled())
    await state.clear()
    await dialog_manager.start(state=MainSG.main,
                               mode=StartMode.RESET_STACK)


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
                await dialog_manager.switch_to(state=MainSG.login)
            else:
                logger.info(f'Getting my_notes by {username} result code: {response.status_code}')
                await callback.message.answer(text=i18n.error())

        except requests.exceptions.RequestException as e:
            logger.info(f'Getting my_notes by {username} error {e}')
            await callback.message.asnwer(text=i18n.server.error())
    else:
        await callback.message.answer(text=i18n.auth.error())
        await dialog_manager.switch_to(state=MainSG.login)


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
                await dialog_manager.switch_to(state=MainSG.login)
            else:
                logger.info(f'Getting my_notes by {username} result code: {response.status_code}')
                await callback.message.answer(text=i18n.error())

        except requests.exceptions.RequestException as e:
            logger.info(f'Getting my_notes by {username} error {e}')
            await callback.message.asnwer(text=i18n.server.error())
    else:
        await callback.message.answer(text=i18n.auth.error())
        await dialog_manager.switch_to(state=MainSG.login)


# При вводе произошла ошибка валидации данных
async def wrong_input(callback: CallbackQuery,
                      widget: ManagedTextInput,
                      dialog_manager: DialogManager,
                      result_list: str):

    logger.info(f'User {callback.from_user.id} fills wrong message')

    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    await callback.answer(text=i18n.unknown.message())
