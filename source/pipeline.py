"""
File for the extract, transform and load functions
"""
from source.connector import Connector

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

    def extract_user_profile(self, user_id: str):
        """
        Function for extracting information for the user profile
        :param user_id: Unique user id for which info has to be extracted

        returns:
            Dictionary of the required fields
        """
        url_extendor = 'info'
        data = self._connection.base_api(url_extendor, id_user = user_id)
        return_dict =  {
            'user_id': user_id,
            'username': data['user']['username'],
            'following': data['user']['following_count'],
            'followers': data['user']['follower_count'],
            'is_private': data['user']['is_private'],
            'is_verified': data['user']['is_verified'],
            'profile_pic_url': data['user']['profile_pic_url'],
            'total_posts': data['user']['media_count']
        }
        return return_dict
