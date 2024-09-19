from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot



def load_config(path: str | None = None) -> Config:
    """
    Load a configuration from a `.env` file.

    The configuration is loaded from the file specified by `path` (if not None)
    or from the current working directory if `path` is None.

    The configuration is returned as an instance of `Config`.

    Parameters
    ----------
    path : str | None
        The path to the `.env` file to load the configuration from.

    Returns
    -------
    Config
        An instance of `Config` containing the configuration.
    """
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))
