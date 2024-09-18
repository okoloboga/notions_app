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


# Регистрация
async def registration_getter(dialog_manager: DialogManager,
                              i18n: TranslatorRunner,
                              bot: Bot,
                              event_from_user: User,
                              **kwargs
                              ) -> dict:
    
    username = event_from_user.username
    
    logger.info(f'User {username} in registration menu')

    return {'registration': i18n.registration(username=username)}


# Авторизация
async def login_getter(dialog_manager: DialogManager,
                       i18n: TranslatorRunner,
                       bot: Bot,
                       event_from_user: User,
                       **kwargs
                       ) -> dict:
    
    username = event_from_user.username
    
    logger.info(f'User {username} in login menu')

    return {'login': i18n.login(username=username)}


# Главное Меню
async def main_getter(dialog_manager: DialogManager,
                      i18n: TranslatorRunner,
                      bot: Bot,
                      event_from_user: User,
                      **kwargs
                      ) -> dict:

    username = event_from_user.username
    
    logger.info(f'User {username} in main menu')

    return {'main_menu': i18n.main.menu(),
            'button_create_note': i18n.button.create.note(),
            'button_my_notes': i18n.button.my.notes()}


'''Создание записи'''
# Ввод заголовка
async def title_getter(dialog_manager: DialogManager,
                       i18n: TranslatorRunner,
                       bot: Bot,
                       event_from_user: User,
                       **kwargs
                       ) -> dict:
    
    username = event_from_user.username
    
    logger.info(f'User {username} filling title')

    return {'fill_title': i18n.fill.title()}


# Ввод содержания
async def content_getter(dialog_manager: DialogManager,
                         i18n: TranslatorRunner,
                         bot: Bot,
                         event_from_user: User,
                         **kwargs
                         ) -> dict:
    
    username = event_from_user.username
    
    logger.info(f'User {username} filling content')

    return {'fill_content': i18n.fill.content()}


# Ввод Тэгов
async def tags_getter(dialog_manager: DialogManager,
                      i18n: TranslatorRunner,
                      bot: Bot,
                      event_from_user: User,
                      **kwargs
                      ) -> dict:
    
    username = event_from_user.username
    
    logger.info(f'User {username} filling tags')

    return {'fill_tags': i18n.fill.tags()}


# Завершение создания записи
async def complete_getter(dialog_manager: DialogManager,
                          i18n: TranslatorRunner,
                          bot: Bot,
                          event_from_user: User,
                          **kwargs
                          ) -> dict:

    username = event_from_user.username
    state: FSMContext = dialog_manager.middleware_data.get('state')
    note = await state.get_data()
    # title = note['title']
    # content = note['content']
    # tags = note['tags']

    logger.info(f'User {username} completing create note:\n{note}')

    return {'complete_note': i18n.complete.note(**note),
            'button_confirm': i18n.button.confirm(),
            'button_cancel': i18n.button.cancel()}






