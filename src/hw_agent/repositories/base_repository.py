from abc import ABC, abstractmethod
from typing import Optional
from hw_agent.models.connection_config_models import ConnectionConfigCreate, ConnectionConfigRead

class BaseRepository(ABC):
    @abstractmethod
    def save_configuration(self, config_id: str, connection_config: ConnectionConfigCreate) -> None:
        """
        Stores the configuration and returns a unique config_id.
        """
        pass

    @abstractmethod
    def get_configuration(self, config_id: str) -> Optional[ConnectionConfigRead]:
        """
        Retrieves the configuration based on config_id.
        """
        pass

    @abstractmethod  
    def get_configurations(self) -> Optional[list[ConnectionConfigRead]] :
        pass


    @abstractmethod
    def delete_configuration(self, config_id: str) -> None:
        """
        Deletes a configuration based on config_id.
        """
        pass

    @abstractmethod
    def clear_all_configurations(self) -> None:
        """
        Clears all configurations.
        """
        pass
