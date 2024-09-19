import logging 

from aiogram import Bot
from aiogram.types import User
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


async def registration_getter(dialog_manager: DialogManager,
                              i18n: TranslatorRunner,
                              bot: Bot,
                              event_from_user: User,
                              **kwargs
                              ) -> dict:
    """
    Getter for registration menu.
    
    Returns:
        dict: Dictionary with registration message for user.
    """
    username = event_from_user.username
    
    logger.info(f'User {username} in registration menu')

    return {'registration': i18n.registration(username=username)}




async def login_getter(dialog_manager: DialogManager,
                       i18n: TranslatorRunner,
                       bot: Bot,
                       event_from_user: User,
                       **kwargs
                       ) -> dict:
    """
    Getter for login menu.
    
    Returns:
        dict: Dictionary with login message for user.
    """
    username = event_from_user.username
    
    logger.info(f'User {username} in login menu')

    return {'login': i18n.login(username=username)}


async def main_getter(dialog_manager: DialogManager,
                      i18n: TranslatorRunner,
                      bot: Bot,
                      event_from_user: User,
                      **kwargs
                      ) -> dict:
    """
    Getter for main menu.
    
    Returns:
        dict: Dictionary with main message for user and buttons.
    """
    username = event_from_user.username
    
    logger.info(f'User {username} in main menu')

    return {'main_menu': i18n.main.menu(),
            'button_create_note': i18n.button.create.note(),
            'button_my_notes': i18n.button.my.notes()}


'''Create Note process'''
async def title_getter(dialog_manager: DialogManager,
                       i18n: TranslatorRunner,
                       bot: Bot,
                       event_from_user: User,
                       **kwargs
                       ) -> dict:
    """
    Getter for title menu.
    
    Returns:
        dict: Dictionary with title message for user.
    """
    username = event_from_user.username
    
    logger.info(f'User {username} filling title')

    return {'fill_title': i18n.fill.title()}


async def content_getter(dialog_manager: DialogManager,
                         i18n: TranslatorRunner,
                         bot: Bot,
                         event_from_user: User,
                         **kwargs
                         ) -> dict:
    """
    Getter for content menu.
    
    Returns:
        dict: Dictionary with content message for user.
    """
    username = event_from_user.username
    
    logger.info(f'User {username} filling content')

    return {'fill_content': i18n.fill.content()}


async def tags_getter(dialog_manager: DialogManager,
                      i18n: TranslatorRunner,
                      bot: Bot,
                      event_from_user: User,
                      **kwargs
                      ) -> dict:
    """
    Getter for tags menu.
    
    Returns:
        dict: Dictionary with tags message for user.
    """
    username = event_from_user.username
    
    logger.info(f'User {username} filling tags')

    return {'fill_tags': i18n.fill.tags()}


async def complete_getter(dialog_manager: DialogManager,
                          i18n: TranslatorRunner,
                          bot: Bot,
                          event_from_user: User,
                          **kwargs
                          ) -> dict:
    """
    Getter for complete menu.
    
    Returns:
        dict: Dictionary with complete message for user and buttons.
    """
    username = event_from_user.username
    state: FSMContext = dialog_manager.middleware_data.get('state')
    note = await state.get_data()
    
    # Get note data from state
    title = note['title']
    content = note['content']
    tags = note['tags']

    logger.info(f'User {username} completing create note:\n'
                f'Title: {title}\n'
                f'Content: {content}\n'
                f'Tags: {tags}')


    return {'complete_note': i18n.complete.note(title=title,
                                                content=content,
                                                tags=tags),
            'button_confirm': i18n.button.confirm(),
            'button_cancel': i18n.button.cancel()}


