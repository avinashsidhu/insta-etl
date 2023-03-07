"""
Connecter to API for extracting data and DB for loading data
"""
import json
import requests
from source.constants import APIConstants

class Connector():
    """
    Class for the conenctor methods.
    """
    def __init__(self, api_key: str):
        """
        Constructor for the Connector class

        :param api_key: API key to access the Rapid API endpoints
        """
        self.api_key = api_key

    def base_api(self, url_extendor: str, **kwargs):
        """
        Function to make the base API call to 
        extract data from Rapid API

        :param url_extendor: Extendor for the API call to add to the base API URL
        :param **kwargs: Keyword arguments to construct the querystring

        returns:
            returns the JSON response from the base API call
        """
        url = f"{APIConstants.BASE_URL}{url_extendor}/"
        headers = {
            APIConstants.HEADER_API_KEY: self.api_key,
            APIConstants.HEADER_API_HOST: APIConstants.API_HOST
        }
        querystring = {}
        for key, value in kwargs.items():
            querystring[key] = value
        response = requests.request(APIConstants.REQUEST_TYPE, url, headers = headers,
                                    params = querystring, timeout = APIConstants.TIMEOUT)
        return json.loads(response.text)
