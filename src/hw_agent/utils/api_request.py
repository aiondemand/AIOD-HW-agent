# util/api_request.py

import requests

from hw_agent.exceptions.custom_exceptions import APIRequestError
from hw_agent.utils.logger import get_logger


class APIRequest:
    """
    Utility class for making API requests.
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = get_logger(self.__class__.__name__)

    def make_request(self, method, endpoint, headers=None, **kwargs):
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        headers.setdefault("User-Agent", "Mozilla/5.0")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=kwargs.get('timeout', 10),
                params=kwargs.get('params'),
                data=kwargs.get('data'),
                json=kwargs.get('json')
            )
            response.raise_for_status()

            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            else:
                return response.content

        except requests.exceptions.HTTPError as http_err:
            error_msg = f"HTTP error occurred: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise APIRequestError(error_msg) from http_err

        except requests.exceptions.Timeout as timeout_err:
            error_msg = "The request timed out"
            self.logger.error(error_msg)
            raise APIRequestError(error_msg) from timeout_err

        except requests.exceptions.RequestException as req_err:
            error_msg = f"Request exception occurred: {req_err}"
            self.logger.error(error_msg)
            raise APIRequestError(error_msg) from req_err

        except Exception as err:
            error_msg = f"An unexpected error occurred: {err}"
            self.logger.error(error_msg)
            raise APIRequestError(error_msg) from err
