# src/hw_agent/services/aiod_metadata_client.py

from hw_agent.dependencies import get_setting_service
from hw_agent.exceptions.custom_exceptions import APIRequestError, AuthenticationError
from hw_agent.models.computational_asset import ComputationalAsset
from hw_agent.services.keycloak_client import KeycloakClient
from hw_agent.services.settings_service import SettingsService
import requests

from hw_agent.utils.api_request import APIRequest
from hw_agent.utils.logger import get_logger

class AIODMetadataClient:
    def __init__(self):
        settings = get_setting_service()
        self.aiod_api_base_url = settings.get('aiod_api_base_url')
        self.aiod_keycloak_client_id = settings.get('aiod_keycloak_client_id')
        self.aiod_keycloak_client_secret = settings.get('aiod_keycloak_client_secret')
        self.aiod_keycloak_auth_url = settings.get('aiod_keycloak_auth_url')
        self.aiod_keycloak_realm = settings.get('aiod_keycloak_realm')

        if not self.aiod_api_base_url:
            raise ValueError("AIOD base URL key must be set in env file under the key AIOD_API_BASE_URL")
        
        self.keycloak_client = KeycloakClient(
            auth_url=self.aiod_keycloak_auth_url,
            realm=self.aiod_keycloak_realm,
            client_id=self.aiod_keycloak_client_id,
            client_secret=self.aiod_keycloak_client_secret
        )
        
        # Instantiate the APIRequestUtil without keycloak_client
        self.api_request = APIRequest(
            base_url=self.aiod_api_base_url
        )
        
        self.logger = get_logger(self.__class__.__name__)

    def create_computational_asset(self, asset_data: ComputationalAsset):
        endpoint = "/computational_assets/v1"
        json_data = asset_data.model_dump(mode="json")

        # Get the token using KeycloakClient
        token = self.keycloak_client.get_keycloak_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        return self.api_request.make_request(
            method='POST',
            endpoint=endpoint,
            headers=headers,
            json=json_data
        )

    def update_asset(self, asset_id, asset_data: ComputationalAsset):
        endpoint = f"/computational_assets/v1/{asset_id}"
        json_data = asset_data.model_dump(mode="json")
        token = self.keycloak_client.get_keycloak_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = self.api_request.make_request(
            method='PUT',
            endpoint=endpoint,
            headers=headers,
            json=json_data
        )

        return response

    def get_asset(self, asset_id):
        endpoint = f"/computational_assets/v1/{asset_id}"

        return self.api_request.make_request(
            method='GET',
            endpoint=endpoint
        )
        
    def get_all_assets(self):
        endpoint = "/computational_assets/v1"

        return self.api_request.make_request(
            method='GET',
            endpoint=endpoint
        )
    
