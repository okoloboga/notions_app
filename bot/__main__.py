import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram_dialog import setup_dialogs
from fluentogram import TranslatorHub
from redis.asyncio.client import Redis

from config import Config, load_config
from dialog import dialog, router, unknown_router
from utils import TranslatorHub, create_translator_hub
from middleware import TranslatorRunnerMiddleware


logger = logging.getLogger(__name__)

# Конфигурация и запуск Бота
async def main():

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
               )
    logger.info('Starting Bot')

    # Config
    storage = RedisStorage(Redis(),
                           key_builder=DefaultKeyBuilder(with_destiny=True))

    # Init Bot in Dispatcher
    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    # i18n init
    translator_hub: TranslatorHub = create_translator_hub()

    # Routers, dialogs, middlewares
    dp.include_routers(dialog, router, unknown_router)

    dp.update.middleware(TranslatorRunnerMiddleware())

    setup_dialogs(dp)

    # Skipping old updates
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, _translator_hub=translator_hub)
    return bot

if __name__ == '__main__':
    asyncio.run(main())
