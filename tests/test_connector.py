"""
Tests for Connector Methods
"""

import unittest
# import requests
# from source.connector import Connector
# from source.constants import APIConstants

class TestConnectorMethods(unittest.TestCase):
    """
    Testing the S3BUcketConnector class
    """
    def base_api(self, url_extendor: str, **kwargs):
        """
        Function to make the base API call to 
        extract data from Rapid API

        :param url_extendor: Extendor for the API call to add to the base API URL
        :param **kwargs: Keyword arguments to construct the parameters

        returns:
            returns the JSON response from the base API call
        """