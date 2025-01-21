import os
from typing import Any
from dotenv import load_dotenv

from hw_agent.core.singleton_meta import SingletonMeta
from hw_agent.utils.logger import get_logger


class SettingsService:
    """
    Service to manage application settings loaded from pyproject.toml.
    """

    def __init__(self):
        self.logger = get_logger("SettingsService")
        self.config = self._initialize()
        
    def _initialize(self):
        # Load .env file if it exists
        load_dotenv(dotenv_path='.env', override=True)


    def get(self, key: str, default=None) -> Any:
        
        # If key is None, default value is returned
        if key is None:
            return default
        
        # Check if key has a not None value and do it uppercase
        key = key.upper()
        
        # First, try to get the value from environment variables
        value = os.environ.get(key)
        if value is not None:
            return value

        # Finally, return the default value
        return default