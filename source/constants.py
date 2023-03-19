"""
File for constants
"""
from enum import Enum

class DBConstants(Enum):
    """
    Class to store the constants for DB connection
    """
    HOST_URL = 'mongodb://localhost:27017/'
    DB_NAME = 'insta-db'
    USER_INFO_COLLECTION = 'user_info'
    POST_INFO_COLLECTION = 'post_info'
    COMMENTS_COLLECTION = 'comments'
    LIKES_COLLECTION = 'likes'
    FOLLOWERS_COLLECTION = 'followers'
    FOLLOWING_COLLECTION = 'following'

class APIConstants(Enum):
    """
    Class for storing API constants
    """
    BASE_URL = 'https://instagram-scraper-2022.p.rapidapi.com/ig'
    API_HOST = 'instagram-scraper-2022.p.rapidapi.com'
    REQUEST_TYPE = 'GET'
    HEADER_API_KEY = 'X-RapidAPI-Key'
    HEADER_API_HOST = 'X-RapidAPI-Host'
    TIMEOUT = 50

class PipelineConstants(Enum):
    """
    Class with constants used in the Pipeline
    """
    PROFILE_INFO_EXTENDOR = 'info'
    FOLLOWERS_EXTENDOR = 'followers'
    FOLLOWING_EXTENDOR = 'following'
    USER_EXTRACT_FIELDS = ['username', 'following_count', 'follower_count',
                           'is_private', 'is_verified', 'profile_pic_url',
                           'media_count']
    POST_INFO_EXTENDOR = 'post_info'
    LIKES_EXTENDOR = 'likes'
    COMMENTS_EXTENDOR = 'comments'
    POSTS_EXTENDOR = 'posts'
    