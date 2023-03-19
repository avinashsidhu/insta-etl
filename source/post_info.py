"""
File for the extracting post level information
"""
import logging
from source.connector import SourceConnector
from source.constants import PipelineConstants


class PostInfo():
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

    def extract_post_info(self, shortcode: str):
        """
        Function to extract post level information
        : param post_shortcode: Unique identifier for the post

        returns:
            Dictionary with required fields
        """
        self._logger.info(
            "Extracting post info for post with %s shortcode", shortcode)
        data = self.__helper_post_info(shortcode)

        user_tag_yn, user_tag_list = self.__helper_user_tag(data)
        num_content = self.__helper_num_content(data)
        return_dict = {
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
        if num_content == 1:
            self._logger.info(
                "Post with %s shortcode has no extra content. Returning info", shortcode)
            return (return_dict, {})
        self._logger.info(
            "Post with %s shortcode has %s extra content. Returning info for those", shortcode, num_content)
        return_tuple = (
            return_dict, self.__extended_post_info(data['id'], data))
        self._logger.info(
            "Returning total content info for post with %s shortcode", shortcode)
        return return_tuple

    def __extended_post_info(self, post_id: str, json_object: str):
        """
        Function to extract extended post info for a post with multiple
        photos/videos in a single post
        :param post_id: Post ID corresponding to the original post
        :param json_object: The API response to search for the info 

        Returns: 
            Dictionary containing the extended post information
        """
        data = json_object['edge_sidecar_to_children']['edges']
        post_content_id = [f'{post_id}[{str(i)}]' for i in range(len(data))]
        content_id = [data[i]['node']['id'] for i in range(len(data))]
        try:
            num_views = [data[i]['node']['video_view_count']
                         for i in range(len(data))]
            url_id = [data[i]['node']['video_url'] for i in range(len(data))]
            is_video = [data[i]['node']['is_video'] for i in range(len(data))]
        except KeyError:
            num_views = [0 for i in range(len(data))]
            url_id = [data[i]['node']['display_url'] for i in range(len(data))]
            is_video = [data[i]['node']['is_video'] for i in range(len(data))]
        return {
            'post_id': post_id,
            'post_content_id': post_content_id,
            'content_id': content_id,
            'url_id': url_id,
            'is_video': is_video,
            'num_views': num_views
        }

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
