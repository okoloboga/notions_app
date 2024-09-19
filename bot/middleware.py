import logging

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub

logger = logging.getLogger(__name__)
    
# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s'
)


class TranslatorRunnerMiddleware(BaseMiddleware):
    """
    Middleware that sets the FluentTranslator for the current user to the event data.
    
    The FluentTranslator is retrieved from the TranslatorHub by the user's locale.
    If the user is not found, the FluentTranslator is not set.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Calls the handler with the FluentTranslator set to the event data.
        
        If the user is not found, the FluentTranslator is not set.
        """
        user: User = data.get('event_from_user')
        
        if user is None:
            return await handler(event, data)
        
        hub: TranslatorHub = data.get('_translator_hub')
        data['i18n'] = hub.get_translator_by_locale(locale=user.language_code)
        return await handler(event, data)
