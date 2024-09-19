from functools import lru_cache
from typing import TypeVar, Type

from pydantic import BaseModel, PostgresDsn
from yaml import load

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

ConfigType = TypeVar("ConfigType", bound=BaseModel)


class DbConfig(BaseModel):
    dsn: PostgresDsn
    is_echo: bool


class Salt(BaseModel):
    key: str


class JWT(BaseModel):
    key: str


@lru_cache(maxsize=1)
def parse_config_file() -> dict:
    """
    Parse a given YAML file to a dictionary.

    The function reads the file, parses it and returns the parsed data.
    The file is expected to be in the same directory as the script.

    Returns:
        dict: The parsed YAML file as a dictionary.

    Raises:
        FileNotFoundError: If the file is not found.
        YAMLError: If the file is not a valid YAML file.
    """
    with open ("config.yaml", "rb") as file:
        config_data = load(file, Loader=SafeLoader)
    return config_data


@lru_cache
def get_config(model: Type[ConfigType],
               root_key: str) -> ConfigType:
    """
    Get a configuration from the YAML file.

    The function reads the YAML file, parses it and returns the parsed data
    as a given model type.

    Args:
        model (Type[ConfigType]): The model that the data should be parsed into.
        root_key (str): The root key in the YAML file to parse from.

    Returns:
        ConfigType: The parsed data as the given model type.

    Raises:
        FileNotFoundError: If the file is not found.
        YAMLError: If the file is not a valid YAML file.
        ValueError: If the root key is not found in the config file.
    """
    config_dict = parse_config_file()
    if root_key not in config_dict:
        error = f"Key {root_key} not found"
        raise ValueError(error)
    return model.model_validate(config_dict[root_key])
