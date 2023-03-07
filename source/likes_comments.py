"""
File for the extracting users who liked and commented on a post
"""
from source.connector import Connector
from source.constants import PipelineConstants


class PostLikesComments():
    """
    class to implement ETL methods
    """

    def __init__(self, api_connection: Connector):
        """
        Constructor for the Instagram pipeline class
        :param connector: Connection to the API calls
        """
        self._connection = api_connection

    def extract_like_users(self, shortcode: str):
        """
        Function to fetch the list of users who liked a given post
        :param shortcode: Unique identifier for the post

        Returns:
            List of users who like the post
        """
        url_extendor = PipelineConstants.LIKES_EXTENDOR.value
        response = self.__helper(url_extendor, shortcode)
        while True:
            user_response = response['data']['shortcode_media']['edge_liked_by']
            users = [user['node']['id'] for user in user_response['edges']]
            if user_response['page_info']['has_next_page']:
                next_page = user_response['page_info']['end_cursor']
                response = self.__helper(url_extendor, shortcode, next_page)
            else:
                break
        return users

    def insta_post_comments(self, shortcode: str):
        """
        Function to fetch the list of users who commented on a given post
        along with the comments they posted
        :param shortcode: Unique identifier for the post

        Returns:
            List of users who commented on a the post along with comment text
        """
        url_extendor = PipelineConstants.COMMENTS_EXTENDOR.value
        response = self.__helper(url_extendor, shortcode)
        while True:
            users_list = [comment['user_id']
                          for comment in response['comments']]
            comments_list = [comment['text']
                             for comment in response['comments']]
            try:
                next_page = response['next_min_id']
                response = self.__helper(shortcode, next_page)
            except KeyError:
                try:
                    next_page = response['end_cursor']
                    response = self.__helper(shortcode, next_page)
                except KeyError:
                    break
        return (users_list, comments_list)

    def __helper(self, url_extendor: str, post_code: str, next_page: str = ""):
        """
        Helper function to fetch the information on followers of a given user
        :param url_extendor: Differentiating extendor for followers or following extractor
        :param next_page: Named argument passed to the base API to signal next list

        returns:
            Function call to the actual base api to fetch followers
        """
        if next_page == "":
            return self._connection.base_api(url_extendor, shortcode=post_code)
        return self._connection.base_api(url_extendor, shortcode=post_code, end_cursor=next_page)
