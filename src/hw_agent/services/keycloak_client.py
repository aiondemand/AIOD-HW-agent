import time
import requests

from hw_agent.utils.logger import get_logger

class AuthenticationError(Exception):
    pass

class KeycloakClient:
    def __init__(self, auth_url, realm, client_id, client_secret):
        self.aiod_keycloak_auth_url = auth_url
        self.aiod_keycloak_realm = realm
        self.aiod_keycloak_client_id = client_id
        self.aiod_keycloak_client_secret = client_secret
        self.token = None
        self.token_expires_at = 0  # Initialize with 0 to force token retrieval
        
        self.logger = get_logger(self.__class__.__name__)

    def get_keycloak_token(self):
        current_time = time.time()

        # Check if the token exists and is still valid
        if self.token and current_time < self.token_expires_at:
            return self.token

        # Request a new token if no valid token exists or token has expired
        token_url = f"{self.aiod_keycloak_auth_url}/realms/{self.aiod_keycloak_realm}/protocol/openid-connect/token"

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.aiod_keycloak_client_id,
            "client_secret": self.aiod_keycloak_client_secret
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
             "User-Agent": 'Mozilla/5.0'
        }

        try:
            response = requests.post(token_url, data=payload, headers=headers)
            response.raise_for_status()

            token_data = response.json()
            self.token = token_data["access_token"]

            # Calculate token expiration time (current time + expires_in seconds)
            expires_in = token_data.get("expires_in", 60)  # Default to 60 seconds if not provided
            self.token_expires_at = current_time + expires_in - 10  # Subtract 10 seconds as a buffer

            return self.token
        except requests.exceptions.HTTPError as e:
            self.logger.error("Failed to get keycloak token. HTTPError:", exc_info=True)
            raise AuthenticationError(f"HTTP error getting token: {response.status_code} - {e}")
        except Exception as e:
            self.logger.error("Failed to get keycloak token. Exception:", exc_info=True)
            raise AuthenticationError(f"Error getting token: {e}")
