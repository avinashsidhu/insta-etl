"""
File for the extract, transform and load functions
"""
from source.connector import Connector
from source.user_info import UserInfo


class InstagramPipeline():
    """
    class to implement ETL methods
    """

    def __init__(self, api_connection: Connector):
        """
        Constructor for the Instagram pipeline class
        :param connector: Connection to the API calls
        """
        self._connection = api_connection

    def extract_per_user(self, user_id: str):
        """
        Function to extract the required fields for a single user ID
        :param user_id: Unique user id for which info has to be extracted
        """
        user_info = UserInfo(self._connection)
        profile_info = user_info.extract_user_profile(user_id)
        # followers = user_info.extract_followers(user_id)
        # following = user_info.extract_following(user_id)
        # return [profile_info, followers, following]
        return profile_info
    