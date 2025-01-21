

from hw_agent.core.singleton_meta import SingletonMeta
from hw_agent.models.computational_asset import ComputationalAsset
from hw_agent.services.aiod_metadata_client import AIODMetadataClient


class CatalogueService(metaclass=SingletonMeta):
    def __init__(self):
        self.aiod_client = AIODMetadataClient()

    def get_computational_asset(self, asset_id: str) -> ComputationalAsset:
        """
        Retrieves a computational asset based on the provided asset_id from the Metadata Catalogue.
        """
        return self.aiod_client.get_asset(asset_id)
    
    
    def create_computational_asset(self, computational_asset: ComputationalAsset):
        """
        Creates a computational asset in the Metadata Catalogue.
        """
        return self.aiod_client.create_computational_asset(computational_asset)
    
                
    def get_all_computational_assets(self) -> list[ComputationalAsset]:
        """
        Retrieves all computational assets from the Metadata Catalogue.
        """
        return self.aiod_client.get_all_assets()

