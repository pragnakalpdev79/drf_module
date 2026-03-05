import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class ExternalAPIService:
    def __init__(self):
        self.base_url = 'https://hp-api.onrender.com/api/'
        self.api_key = settings.EXTERNAL_API_KEY

    def get_data(self,endpoint):
        headers = {
            'Authorization' : f'Bearer {self.api_key}',
            'Content-Type' : 'application/json',
        }
        try:
            response = requests.get(
                    f'{self.base_url}/{endpoint}',
                    headers=headers,
                    timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout Calling {endpoint}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error calling {endpoint} : {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request errro calling {endpoint}: {e}")
            raise

        
    def post_data(self,endpointg,data):
        headers = {
                'Authorization' : f"Bearer {self.api_key}",
                'Content-Type': 'application/json',
            }
        response = requests.post(
                f'{self.base_url}/endpoinr',
                headers=headers,
                json=data,
                timeout=10
            )
        response.raise_for_status()
        return response.json()