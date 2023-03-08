"""
Connecter to API for extracting data and DB for loading data
"""
import os
import json
import logging
import requests
from source.constants import APIConstants, PipelineConstants


class Connector():
    """
    Class for the conenctor methods.
    """

    def __init__(self, api_key: str):
        """
        Constructor for the Connector class

        :param api_key: API key to access the Rapid API endpoints
        """
        self.api_key = os.environ[api_key]
        self._logger = logging.getLogger(__name__)

    def base_api(self, url_extendor: str, **kwargs):
        """
        Function to make the base API call to 
        extract data from Rapid API

        :param url_extendor: Extendor for the API call to add to the base API URL
        :param **kwargs: Keyword arguments to construct the parameters

        returns:
            returns the JSON response from the base API call
        """
        url = f"{APIConstants.BASE_URL.value}{url_extendor}/"
        headers = {
            APIConstants.HEADER_API_KEY.value: self.api_key,
            APIConstants.HEADER_API_HOST.value: APIConstants.API_HOST.value
        }
        parameters = {}
        for key, value in kwargs.items():
            parameters[key] = value
        response = requests.request(method=APIConstants.REQUEST_TYPE.value, url=url,
                                    headers=headers, params=parameters,
                                    timeout=APIConstants.TIMEOUT.value)
        # The API for comments is throwing HTTP 500 error randomly
        while url_extendor == PipelineConstants.COMMENTS_EXTENDOR.value and response.status_code == 500:
            response = requests.request(method=APIConstants.REQUEST_TYPE.value, url=url,
                                        headers=headers, params=parameters,
                                        timeout=APIConstants.TIMEOUT.value)

        return json.loads(response.text)
