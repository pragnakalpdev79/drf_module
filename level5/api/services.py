import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ExternalAPIService:
    def __init__(self):
        self.base_url = 'https://hp-api.onrender.com/api/characters'
        self.api_key = settings.EXTERNAL_API_KEY

    def get_data(self,endpoint,data):
        try:
            response = requests.get(
                f'{self.base_url}/{endpoint}',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling {endpoint}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error calling {endpoint} : {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error calling {endpoint}: {e}")
            
    