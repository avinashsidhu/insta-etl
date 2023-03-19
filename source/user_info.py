"""
File for the extracting user level information
"""
import logging
from source.connector import SourceConnector
from source.constants import PipelineConstants


class UserInfo():
    """
    class to implement ETL methods
    """

    def __init__(self, api_connection: SourceConnector):
        """
        Constructor for the Instagram pipeline class
        :param connector: Connection to the API calls
        """
        self._connection = api_connection
        self._logger = logging.getLogger(__name__)

    def extract_user_profile(self, user_id: str):
        """
        Function for extracting information for the user profile
        :param user_id: Unique user id for which info has to be extracted

        returns:
            Dictionary of the required fields
        """
        self._logger.info("Extracting profile info for %s user", user_id)
        url_extendor = PipelineConstants.PROFILE_INFO_EXTENDOR.value
        data = self._connection.base_api(url_extendor, id_user=user_id)
        return_dict = {key: data['user'][key]
                       for key in PipelineConstants.USER_EXTRACT_FIELDS.value}
        self._logger.info("Extracted profile info for %s user", user_id)
        return return_dict

    def extract_followers(self, user_id: str):
        """
        Function to extract all the followers for a given user ID
        :param user_id: Unique user id for which info has to be extracted
        :param url_extendor: Differentiating extendor for followers or following extractor

        Returns:
            List of all the followers for a given user ID
        """
        self._logger.info("Extracting followers for %s user", user_id)
        url_extendor = PipelineConstants.FOLLOWERS_EXTENDOR.value
        followers = self.__user_list_from_api_call(user_id, url_extendor)
        self._logger.info("Extracted all followers for %s user", user_id)
        return followers

    def extract_following(self, user_id: str):
        """
        Function to extract all the following for a given user ID
        :param user_id: Unique user id for which info has to be extracted
        :param url_extendor: Differentiating extendor for followers or following extractor

        Returns:
            List of all the following for a given user ID
        """
        self._logger.info("Extracting following for %s user", user_id)
        url_extendor = PipelineConstants.FOLLOWING_EXTENDOR.value
        followers = self.__user_list_from_api_call(user_id, url_extendor)
        self._logger.info("Extracted all following for %s user", user_id)
        return followers

    def __user_list_from_api_call(self, user_id: str, url_extendor: str):
        """
        Function to fetch all followers/following of a given user
        :param user_id: ID of the user whose followers are to be extracted
        :param url_extendor: Differentiating extendor for followers or following extractor

        Returns:
            Dataframe containing followers of a given user
        """
        user_list = []
        response = self.__helper_user_list(url_extendor, user_id)
        while True:
            self._logger.info("Extracted %s %s for %s user", str(
                len(user_list)), url_extendor, user_id)
            user_list = user_list + [user['pk']
                                      for user in response['users']]
            try:
                next_page = response['next_max_id']
                response = self.__helper_user_list(
                    url_extendor, user_id, next_page)
            except KeyError:
                break
        return user_list

    def __helper_user_list(self, url_extendor: str, user_id: str, next_page: str = ""):
        """
        Helper function to fetch the information on followers of a given user
        as RAPID API only allows 100 followers/following to be extracted at once
        :param url_extendor: Differentiating extendor for followers or following extractor
        :param next_page: Named argument passed to the base API to signal next list

        returns:
            Function call to the actual base api to fetch followers
        """
        if next_page == "":
            return self._connection.base_api(url_extendor, id_user=user_id)
        return self._connection.base_api(url_extendor, id_user=user_id, next_max_id=next_page)
