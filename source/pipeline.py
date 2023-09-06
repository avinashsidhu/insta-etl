"""
File for the extract, transform and load functions
"""
import logging
from datetime import datetime
import pandas as pd
from source.connector import SourceConnector, DestinationConnector
from source.user_info import UserInfo
from source.post_info import PostInfo
from source.likes_comments import PostLikesComments
from source.constants import PipelineConstants


class InstagramPipeline():
    """
    class to implement ETL methods
    """

    def __init__(self, api_connection: SourceConnector, db_connection: DestinationConnector):
        """
        Constructor for the Instagram pipeline class
        :param connector: Connection to the API calls
        """
        self._connection = api_connection
        self._db = db_connection
        self._logger = logging.getLogger(__name__)

    def ETL_users(self, path_to_user_ids: str, column_name:str, time_to_process_from: str, time_format: str):
        """
        Function to start the ETL process for processing user information
        :param path_to_user_ids: path to the csv file storing user_ids
        :param time_to_process_from: time from when the data should be processed
        :param time_format: time format for processing
        """
        user_list = pd.read_csv(path_to_user_ids)[column_name].to_list()
        time = datetime.strptime(time_to_process_from, time_format)
        for user in user_list:
            try:
                self.ETL_per_user(user, time)
            except:
                self._logger.info('Data for user with %s user_id could not be collected', user)

    def ETL_posts(self, path_to_shortcodes: str, column_name:str):
        """
        Function to start the ETL process for processing user information
        :param path_to_user_ids: path to the csv file storing user_ids
        :param time_to_process_from: time from when the data should be processed
        :param time_format: time format for processing
        """
        shortcodes_list = pd.read_csv(path_to_shortcodes)[column_name].to_list()
        for shortcode in shortcodes_list:
            try:
                self.ETL_per_post(shortcode)
            except:
                self._logger.info('Data for post with %s shortcode could not be collected', shortcode)

    def ETL_per_user(self, user_id: str, time: datetime):
        """
        Function to extract the information for single user ID
        and store it in the mongoDB database
        """
        response = self.extract_per_user(user_id, time)
        self.load_per_user(user_id, response, time)
        return True
    
    def ETL_per_post(self, shortcode: str):
        """
        Function to extract the information for single user ID
        and store it in the mongoDB database
        """
        response = self.extract_per_post(shortcode)
        self.load_per_post(shortcode, response)
        return True

    def load_per_user(self, user_id: str, response: list, time: datetime):
        """
        Function to load the information in the mongoDB
        database
        :param user_id: Unique user id for which info has to be extracted
        """
        self._logger.info(
            'Loading info for %s user since %s time into MongoDB', user_id, time)
        # profile_info, followers, following, postids, shortcodes, post_infos, likes, comments = response
        profile_info, followers, following, post_ids, shortcodes  = response
        current_time = datetime.strftime(datetime.today(), "%Y%m%d")
        self._db.write_to_s3(storing_key = f'posts/{current_time}/{user_id}.json', info = profile_info, 
                                followers = followers, following = following,
                                postIDs = post_ids, post_shortcodes = shortcodes)
        # self._db.write_df_to_s3(
        #     DBConstants.USER_INFO_COLLECTION.value, userID=user_id, info=profile_info)
        # self._db.write_df_to_s3(
        #     DBConstants.FOLLOWERS_COLLECTION.value, userID=user_id, followers=followers)
        # self._db.write_df_to_s3(
        #     DBConstants.FOLLOWING_COLLECTION.value, userID=user_id, following=following)
        # self._db.insert_into_collection(DBConstants.POST_INFO_COLLECTION.value,
        #                                 userID=user_id, postID=postids, shortcode=shortcodes, info=post_infos)
        # for postid, like in zip(postids, likes):
        #     self._db.insert_into_collection(
        #         DBConstants.LIKES_COLLECTION.value, userID=user_id, postID=postid, likes=like)
        # for postid, comment in zip(postids, comments):
        #     self._db.insert_into_collection(
        #         DBConstants.COMMENTS_COLLECTION.value, userID=user_id, postID=postid, comments=comment)
        self._logger.info(
            'Loaded info for %s user since %s time into MongoDB', user_id, time)
        return True
    
    def load_per_post(self, shortcode: str, response: list):
        """
        Function to load the information in the mongoDB
        database
        :param user_id: Unique user id for which info has to be extracted
        """
        self._logger.info(
            'Storing info for post with shortcode %s to s3', shortcode)
        # profile_info, followers, following, postids, shortcodes, post_infos, likes, comments = response
        post_info, likes, comments  = response
        current_time = datetime.strftime(datetime.today(), "%Y%m%d")
        self._db.write_to_s3(storing_key = f'posts/{current_time}/{shortcode}.json', info = post_info, 
                                likes = likes, comments = comments)

    def extract_per_user(self, user_id: str, time: datetime):
        """
        Function to extract the required fields for a single user ID
        :param user_id: Unique user id for which info has to be extracted
        :param time: Time since the posts have to be extracted.

        Returns:
            list of all fields that are required
        """
        user = UserInfo(self._connection)
        profile_info = user.extract_user_profile(user_id)
        followers = user.extract_followers(user_id)
        following = user.extract_following(user_id)
        postids, shortcodes = self.get_all_posts_user(user_id, time)
        return [profile_info, followers, following, postids, shortcodes]
        
        # post = PostInfo(self._connection)
        # post_infos = [post.extract_post_info(
        #     shortcode) for shortcode in shortcodes]

        # likes_comments = PostLikesComments(self._connection)
        # likes = [likes_comments.extract_like_users(
        #     shortcode) for shortcode in shortcodes]
        # comments = [likes_comments.extract_post_comments(
        #     shortcode) for shortcode in shortcodes]

        # return [profile_info, followers, following, postids, shortcodes, post_infos, likes, comments]
    
    def extract_per_post(self, shortcode: str):
        """
        Function to extract the required fields for a single user ID
        :param user_id: Unique user id for which info has to be extracted
        :param time: Time since the posts have to be extracted.

        Returns:
            list of all fields that are required
        """
        post = PostInfo(self._connection)
        post_info = post.extract_post_info(shortcode)
        likes_comments = PostLikesComments(self._connection)
        likes = likes_comments.extract_like_users(shortcode)
        comments = likes_comments.extract_post_comments(shortcode)
        return [post_info, likes, comments]

    def get_all_posts_user(self, user_id: str, time: datetime):
        """
        Function to get all posts from a user since a given datetime
        :param user_id: Unique user id for which info has to be extracted
        :param time: Time since the posts have to be extracted.

        Returns:
            Tuple containing the post IDs and shortcodes of the posts
            since the given time
        """
        self._logger.info(
            'Fetching all posts for %s user since %s time', user_id, time)
        response = self.__helper_posts(
            user_id)['data']['user']['edge_owner_to_timeline_media']
        break_out_flag = False
        post_list, sc_list = [], []
        while True:
            self._logger.info("Extracted %s posts for %s user",
                              str(len(post_list)), user_id)
            for i in range(len(response['edges'])):
                if time > datetime.fromtimestamp(response['edges'][i]['node']['taken_at_timestamp']):
                    break_out_flag = True
                else:
                    post_list.append(response['edges'][i]['node']['id'])
                    sc_list.append(response['edges'][i]['node']['shortcode'])
            if break_out_flag:
                break
            try:
                next_page = response['page_info']['end_cursor']
                response = self.__helper_posts(user_id, next_page)[
                    'data']['user']['edge_owner_to_timeline_media']
            except KeyError:
                break
        self._logger.info(
            'Fetched all posts for %s user since %s time', user_id, time)
        return (post_list, sc_list)

    def __helper_posts(self, user_id: str, next_page: str = ""):
        """
        Helper function to get posts at one time. Rapid API restricts
        the number of posts that can be fetched at once.
        :param user_id: Unique user id for which info has to be extracted
        :param next_page: Named argument passed to the base API to signal next list

        Returns:
            Call to the base API function to get the posts
        """
        url_extendor = PipelineConstants.POSTS_EXTENDOR.value
        if next_page == "":
            return self._connection.base_api(url_extendor, id_user=user_id)
        return self._connection.base_api(url_extendor, id_user=user_id, end_cursor=next_page)
