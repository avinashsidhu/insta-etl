"""
File for the extract, transform and load functions
"""
from source.connector import Connector
from source.constants import PipelineConstants


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
        profile_info = self.extract_user_profile(user_id)
        followers = self.extract_followers(user_id)
        following = self.extract_following(user_id)
        return [profile_info, followers, following]

    def extract_user_profile(self, user_id: str):
        """
        Function for extracting information for the user profile
        :param user_id: Unique user id for which info has to be extracted

        returns:
            Dictionary of the required fields
        """
        url_extendor = PipelineConstants.PROFILE_INFO_EXTENDOR.value
        data = self._connection.base_api(url_extendor, id_user=user_id)
        return {key: data['user'][key] for key in PipelineConstants.USER_EXTRACT_FIELDS.value}

    def extract_followers(self, user_id: str):
        """
        Function to extract all the followers for a given user ID
        :param user_id: Unique user id for which info has to be extracted
        :param url_extendor: Differentiating extendor for followers or following extractor

        Returns:
            List of all the followers for a given user ID
        """
        url_extendor = PipelineConstants.FOLLOWERS_EXTENDOR.value
        return self.__user_list_from_api_call(user_id, url_extendor)

    def extract_following(self, user_id: str):
        """
        Function to extract all the following for a given user ID
        :param user_id: Unique user id for which info has to be extracted
        :param url_extendor: Differentiating extendor for followers or following extractor

        Returns:
            List of all the following for a given user ID
        """
        url_extendor = PipelineConstants.FOLLOWING_EXTENDOR.value
        return self.__user_list_from_api_call(user_id, url_extendor)

    def extract_post_info(self, shortcode: str):
        """
        Function to extract post level information
        : param post_shortcode: Unique identifier for the post

        returns:
            Dictionary with required fields
        """
        data = self.__helper_post_info(shortcode)

        user_tag_yn, user_tag_list = self.__helper_user_tag(data)
        num_content = self.__helper_num_content(data)

        return {
            'post_id': data['id'],
            'taken_at_timestamp': data['taken_at_timestamp'],
            'user_id': data['owner']['id'],
            'text': data['edge_media_to_caption']['edges'][0]['node']['text'],
            'hashtags': [tag[1:] for tag in data['edge_media_to_caption']
                         ['edges'][0]['node']['text'].split(" ") if tag.startswith('#')],
            'hide_like': data['like_and_view_counts_disabled'],
            'num_likes': data['edge_media_preview_like']['count'],
            'num_comments': data['edge_media_to_comment']['count'],
            'display_url': data['display_url'],
            'user_tag_yn': user_tag_yn,
            'user_tag_list': user_tag_list,
            'num_content': num_content
        }

    def __user_list_from_api_call(self, user_id: str, url_extendor: str):
        """
        Function to fetch followers of a given user
        :param user_id: ID of the user whose followers are to be extracted
        :param url_extendor: Differentiating extendor for followers or following extractor

        Returns:
            Dataframe containing followers of a given user
        """
        user_list = []
        response = self.__helper_user_list(url_extendor, user_id)
        while True:
            user_list = user_list + [(user['pk']
                                      for user in response['users'])]
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
        :param url_extendor: Differentiating extendor for followers or following extractor
        :param next_page: Named argument passed to the base API to signal next list

        returns:
            Function call to the actual base api to fetch followers
        """
        if next_page == "":
            return self._connection.base_api(url_extendor, id_user=user_id)
        return self._connection.base_api(url_extendor, id_user=user_id, next_max_id=next_page)

    def __helper_num_content(self, json_object: dict):
        """
        Function to find the number of photos/videos in a post
        :param json_object: The API response to search for the info 

        Returns:
            Number of photos/videos in a post
        """
        if "edge_sidecar_to_children" not in json_object:
            return 1
        return len(json_object['edge_sidecar_to_children']['edges'])

    def __helper_user_tag(self, json_object: dict):
        """
        Function to check whether a post has tagged users or not,
        if yes, then the number of users tagged are also found
        :param json_object: The API response to search for the info 

        returns:
            Boolean value indicating whether users are tagged or not
            along with list of tagged users, if any
        """
        if len(json_object['edge_media_to_tagged_user']) == 0:
            return (False, [])
        return (True, [user['node']['user']['id']
                       for user in json_object['edge_media_to_tagged_user']['edges']])

    def __helper_post_info(self, post_shortcode: str):
        """
        Helper function to get the post level information from the RAPID API
        : param post_shortcode: Unique identifier for the post

        returns:
            Call to the base API
        """
        url_extendor = PipelineConstants.POST_INFO_EXTENDOR.value
        return self._connection.base_api(url_extendor, shortcode=post_shortcode)
