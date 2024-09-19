import logging
import requests

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
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

r = aioredis.Redis(host='redis', port=6379, db=0)


@router.message(CommandStart())
async def command_start_getter(message: Message,
                               dialog_manager: DialogManager):
    """
    Handler for /start command.

    This handler is responsible for checking if the user exists in the database.
    If the user exists, it sends him to the login menu.
    If the user does not exist, it sends him to the registration menu.
    """
    username = message.from_user.username

    logger.info(f'User {username} start Bot')

    response = await login(username=username,
                           password='')
    logger.info(f'Is user {username} exists {response.status_code}?')

    if response.status_code == 200:
        # User exists, go to login menu
        await dialog_manager.start(state=MainSG.login)
    else:
        # User does not exist, go to registration menu
        await dialog_manager.start(state=MainSG.registration)


async def registration_result(message: Message,
                              widget: ManagedTextInput,
                              dialog_manager: DialogManager,
                              password: str):
    """
    Handler for registration result.

    This handler is responsible for processing the registration result.
    If the registration is successful, it sends the user to the login menu.
    If the registration is not successful, it sends the user to the registration
    menu with an error message.
    """
    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')

    logger.info(f'User {username} in registration process')

    response = await new_user(username, password)
    
    logger.info(f'Registration result: {response}')

    if response == 200:
        # Registration is successful, go to login menu
        await message.answer(text=i18n.registration.complete())
        await dialog_manager.switch_to(state=MainSG.login)
    else:
        # Registration is not successful, go to registration menu with error
        await message.answer(text=i18n.already.registred())
        await dialog_manager.switch_to(state=MainSG.registration)


async def login_result(message: Message,
                       widget: ManagedTextInput,
                       dialog_manager: DialogManager,
                       password: str):
    """
    Handler for login result.

    This handler is responsible for processing the login result.
    If the login is successful, it sends the user to the main menu.
    If the login is not successful, it sends the user to the login
    menu with an error message.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    r = aioredis.Redis(host='redis', port=6379, db=0)
    
    logger.info(f'User {username} in login process')

    response = await login(username, password)

    logger.info(f'Users login result is {response.text}')

    if response.status_code == 200:
        # Login is successful, save the token in Redis
        # and send the user to the main menu
        await r.set(str(user_id), (response.json())['password'], ex=1800)
        await dialog_manager.switch_to(state=MainSG.main)
    else:
        # Login is not successful, go to login menu with error
        await message.answer(text=i18n.wrong.password())


'''Create Note process'''
async def create_note(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):
    """
    Handler for "Create Note" button.

    This handler is responsible for switching the state to MainSG.title,
    which is the state for entering the note title.
    """    
    username = callback.from_user.username
    logger.info(f'User {username} entered create_note')
    
    # Switch to title state
    await dialog_manager.switch_to(state=MainSG.title)


async def check_title(message: Message,
                      widget: ManagedTextInput,
                      dialog_manager: DialogManager,
                      title: str):
    """
    Handler for checking the title of the note.

    This handler is responsible for checking the title of the note.
    If the title is correct, it switches the state to MainSG.content.
    If the title is not correct, it sends an error message to the user.
    """
    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')

    logger.info(f'User {username} create new note with title: {title}')

    # Check if the title is correct
    if len(title) < 15:
        # Title is correct, switch to content state
        await state.update_data(title=title)
        await dialog_manager.switch_to(state=MainSG.content)
    else:
        # Title is not correct, send error message
        await message.answer(text=i18n.toolong.title())


async def check_content(message: Message,
                        widget: ManagedTextInput,
                        dialog_manager: DialogManager,
                        content: str):
    """
    Handler for checking the content of the note.

    This handler is responsible for checking the content of the note.
    If the content is correct, it switches the state to MainSG.tags.
    If the content is not correct, it sends an error message to the user.
    """
    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')

    logger.info(f'User {username} create new note with content:\n{content}')

    # Check if the content is correct
    if len(content) < 700:
        # Content is correct, switch to tags state
        await state.update_data(content=content)
        await dialog_manager.switch_to(state=MainSG.tags)
    else:
        # Content is not correct, send error message
        await message.answer(text=i18n.toolong.content())


async def check_tags(message: Message,
                     widget: ManagedTextInput,
                     dialog_manager: DialogManager,
                     tags: str):
    """
    Handler for checking the tags of the note.

    This handler is responsible for checking the tags of the note.
    If the tags are correct, it switches the state to MainSG.complete.
    If the tags are not correct, it sends an error message to the user.
    """
    username = message.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')
    
    logger.info(f'User {username} create new note with tags: {tags}')

    # Split the tags into a list
    tags_list = tags.split(' ')

    # Check if the count of tags is correct
    if len(tags_list) < 6:
        # Tags are correct, switch to complete state
        await state.update_data(tags=tags)
        await dialog_manager.switch_to(state=MainSG.complete)
    else:
        # Tags are not correct, send error message
        await message.answer(text=i18n.toolong.tags())


async def confirm(callback: CallbackQuery,
                  button: Button,
                  dialog_manager: DialogManager):
    """
    Handler for the confirm button.

    This handler is responsible for creating a new note with the completed data.
    If the creation is successful, it sends the user a success message.
    If the creation is not successful, it sends the user an error message
    with the error code.
    """
    user_id = callback.from_user.id
    username = callback.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')
    completed_note = await state.get_data()
    r = aioredis.Redis(host='redis', port=6379, db=0)

    logger.info(f'User {username} complete note: {completed_note}')

    if await r.exists(user_id) != 0:
        token = str(await r.get(user_id), encoding='utf-8')

        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await new_note(data=completed_note,
                                      headers=headers)
            if response.status_code == 200:
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
            await callback.message.answer(text=i18n.server.error())
    else:
        await callback.message.answer(text=i18n.auth.error())
        await dialog_manager.switch_to(state=MainSG.login)


async def cancel(callback: CallbackQuery,
                 button: Button,
                 dialog_manager: DialogManager):
    """
    Handler for the cancel button.

    This handler is responsible for canceling the note creation process.
    It clears the state and starts the main menu.
    """
    username = callback.from_user.username
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    state: FSMContext = dialog_manager.middleware_data.get('state')

    logger.info(f'Canceling Note create by user {username}')

    # Send the user a message that the note creation was canceled
    await callback.message.answer(text=i18n.canceled())

    # Clear the state
    await state.clear()

    # Start the main menu
    await dialog_manager.start(state=MainSG.main,
                               mode=StartMode.RESET_STACK)


async def my_notes(callback: CallbackQuery,
                   button: Button,
                   dialog_manager: DialogManager):
    """
    Handler for the my_notes button.

    This handler is responsible for getting the list of notes for the current user.
    It checks if the user is authenticated and if the user has any notes.
    If the user is authenticated and has any notes, it shows the list of notes.
    If the user is not authenticated or does not have any notes, it shows the appropriate error message.
    """
    user_id = callback.from_user.id
    username = callback.from_user.username
    logger.info(f'User {username} get notes list')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')    
    r = aioredis.Redis(host='redis', port=6379, db=0)

    if await r.exists(user_id) != 0:
        token = str(await r.get(user_id), encoding='utf-8')

        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await notes(headers)

            if response.status_code == 200:

                logger.info(f'Count of notes: {len(response.json())}')

                if len(response.json()) != 0:
                    logger.info(f'Getting my_notes by {username} result code: 200')
                    for note in response.json():
                        await callback.message.answer(text=i18n.shownote(title=note['title'],
                                                                         content=note['content'],
                                                                         tags=note['tags']
                                                                         )
                                                      )
                else:
                    await callback.message.answer(text=i18n.no.notes())
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
            await callback.message.answer(text=i18n.server.error())
    else:
        await callback.message.answer(text=i18n.auth.error())
        await dialog_manager.switch_to(state=MainSG.login)


async def tags_notes_list(message: Message,
                          widget: ManagedTextInput,
                          dialog_manager: DialogManager,
                          tag: str):
    """
    Handler for the tags_notes_list button.

    This handler is responsible for getting the list of notes for the current user
    by specified tag.
    It checks if the user is authenticated and if the user has any notes.
    If the user is authenticated and has any notes, it shows the list of notes.
    If the user is not authenticated or does not have any notes, it shows the appropriate error message.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    logger.info(f'User {username} get notes list by tag')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')    
    r = aioredis.Redis(host='redis', port=6379, db=0)

    # Check if the user is authenticated
    if await r.exists(user_id) != 0:
        token = str(await r.get(user_id), encoding='utf-8')

        # Try to get the list of notes for the user
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await notes_tag(tag, headers)

            # Check if the response was successful
            if response.status_code == 200:

                logger.info(f'Count of notes: {len(response.json())}')
                
                # If the user has any notes, show the list of notes
                if len(response.json()) != 0:
                    logger.info(f'Getting my_notes by {username} result code: 200')
                    for note in response.json():
                        await message.answer(text=i18n.shownote(title=note['title'],
                                                                content=note['content'],
                                                                tags=note['tags']
                                                                )
                                             )
                # If the user does not have any notes, show an appropriate error message
                else:
                    await message.answer(text=i18n.no.notes())
            # If the response was not successful, check if the user has a valid token
            elif response.status_code == 401:
                logger.info(f'Getting my_notes by {username} result code: 401')
                await message.answer(text=i18n.invalid.token())
                await r.delete(user_id)
                await dialog_manager.switch_to(state=MainSG.login)
            # If the response was not successful, show an appropriate error message
            else:
                logger.info(f'Getting my_notes by {username} result code: {response.status_code}')
                await message.answer(text=i18n.error())

        # If there was an error while getting the list of notes, show an appropriate error message
        except requests.exceptions.RequestException as e:
            logger.info(f'Getting my_notes by {username} error {e}')
            await message.answer(text=i18n.server.error())
    # If the user is not authenticated, show an appropriate error message
    else:
        await message.answer(text=i18n.auth.error())
        await dialog_manager.switch_to(state=MainSG.login)


async def wrong_input(callback: CallbackQuery,
                      widget: ManagedTextInput,
                      dialog_manager: DialogManager,
                      result_list: str):
    """
    Handler for wrong input.

    This handler is responsible for processing the wrong input.
    It sends the user an error message.
    """
    logger.info(f'User {callback.from_user.id} fills wrong message')

    # Get the translator from the dialog manager
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')

    # Send the user an error message
    await callback.answer(text=i18n.wrong.input())
