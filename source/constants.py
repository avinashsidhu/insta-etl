"""
File for constants
"""
from enum import Enum

class APIConstants(Enum):
    """
    Class for storing API constants
    """
    BASE_URL = 'https://instagram-scraper-2022.p.rapidapi.com/ig/'
    API_HOST = 'instagram-scraper-2022.p.rapidapi.com'
    REQUEST_TYPE = 'GET'
    HEADER_API_KEY = 'X-RapidAPI-Key'
    HEADER_API_HOST = 'X-RapidAPI-Host'
    TIMEOUT = 5
    