"""
File for the extracting users who liked and commented on a post
"""
import logging
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
        self._logger = logging.getLogger(__name__)

    def extract_like_users(self, shortcode: str):
        """
        Function to fetch the list of users who liked a given post
        :param shortcode: Unique identifier for the post

        Returns:
            List of users who like the post
        """
        self._logger.info("Extracting likes for the post with %s shortcode", shortcode)
        url_extendor = PipelineConstants.LIKES_EXTENDOR.value
        response = self.__helper(url_extendor, shortcode)
        users = []
        while True:
            self._logger.info("Extracted %s likes for %s post", str(len(users)), shortcode)
            user_response = response['data']['shortcode_media']['edge_liked_by']
            users = users+ [user['node']['id'] for user in user_response['edges']]
            if user_response['page_info']['has_next_page']:
                next_page = user_response['page_info']['end_cursor']
                response = self.__helper(url_extendor, shortcode, next_page)
            else:
                break
        self._logger.info("Likes for the post with %s shortcode extracted", shortcode)
        return users

    def extract_post_comments(self, shortcode: str):
        """
        Function to fetch the list of users who commented on a given post
        along with the comments they posted
        :param shortcode: Unique identifier for the post

        Returns:
            List of users who commented on a the post along with comment text
        """
        self._logger.info("Extracting comments for the post with %s shortcode", shortcode)
        url_extendor = PipelineConstants.COMMENTS_EXTENDOR.value
        response = self.__helper(url_extendor, shortcode)
        users_list, comments_list = [], []
        while True:
            self._logger.info("Extracted %s comments for %s post", str(len(users_list)), shortcode)
            for comment in response['comments']:
                if isinstance(comment, dict):
                    users_list.append(comment['user_id'])
                    comments_list.append(comment['text'])
                if int(comment['child_comment_count']) >= 1:
                    for child_comment in comment['preview_child_comments']:
                        users_list.append(child_comment['user']['pk'])
                        comments_list.append(child_comment['text'])
            try:
                next_page = response['next_min_id']
                response = self.__helper(shortcode, next_page)
            except KeyError:
                try:
                    next_page = response['end_cursor']
                    response = self.__helper(shortcode, next_page)
                except KeyError:
                    break
        self._logger.info("Comments for the post with %s shortcode extracted", shortcode)
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
