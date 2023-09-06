"""
Connecter to API for extracting data and DB for loading data
"""
import os
import json
import logging
import requests
# import pymongo
import boto3
from source.constants import APIConstants, PipelineConstants


class SourceConnector():
    """
    Class for the conenctor methods.
    """
    def __init__(self, api_key: str):
        """
        Constructor for the Connector class

        :param api_key: API key to access the Rapid API endpoints
        """
        self.api_key = os.environ[api_key]
        self._logger = logging.getLogger(__name__)

    def base_api(self, url_extendor: str, **kwargs):
        """
        Function to make the base API call to 
        extract data from Rapid API

        :param url_extendor: Extendor for the API call to add to the base API URL
        :param **kwargs: Keyword arguments to construct the parameters

        returns:
            returns the JSON response from the base API call
        """
        url = f"{APIConstants.BASE_URL.value}/{url_extendor}/"
        headers = {
            APIConstants.HEADER_API_KEY.value: self.api_key,
            APIConstants.HEADER_API_HOST.value: APIConstants.API_HOST.value
        }
        parameters = {key: value for key, value in kwargs.items()}
        response = requests.request(method = APIConstants.REQUEST_TYPE.value, url = url,
                                    headers = headers, params = parameters,
                                    timeout = APIConstants.TIMEOUT.value)
        # The API for comments is throwing HTTP 500 error randomly
        while url_extendor == PipelineConstants.COMMENTS_EXTENDOR.value and response.status_code == 500:
            response = requests.request(method = APIConstants.REQUEST_TYPE.value, url = url,
                                        headers = headers, params = parameters,
                                        timeout = APIConstants.TIMEOUT.value)

        return json.loads(response.text)

class DestinationConnector():
    """
    Class for the conenctor methods.
    """
    # def __init__(self):
    #     """
    #     Constructor for the Connector class
    #     """
    #     self._logger = logging.getLogger(__name__)
    #     self._client = pymongo.MongoClient(DBConstants.HOST_URL.value)
    #     self._db = self._client[DBConstants.DB_NAME.value]
    def __init__(self, access_key: str, secret_key: str, endpoint_url: str, bucket: str):
        """
        Constructor for S3BucketConnector

        :param access_key: access key for accessing S3
        :param secret_key: secret key for accessing S3
        :param endpoint_url: endpoint url to S3
        :param bucket: S3 bucket name
        """
        self._logger = logging.getLogger(__name__)
        self.endpoint_url = endpoint_url
        self._s3 = boto3.resource('s3', aws_access_key_id = access_key, aws_secret_access_key = secret_key)
        self._bucket = bucket
    
    def write_to_s3(self, storing_key: str, **kwargs):
        """
        writing pandas dataframe to s3
        supported formats: csv, parquet

        :param dataframe: Pandas dataframe to be written
        :param key: key to the saved file
        :para file_format: format of the file to be saved
        """
        self._logger.info('Writing to s3 with key %s', storing_key)
        data = {key: value for key, value in kwargs.items()}
        # s3_object = self._s3.Object(self._bucket, storing_key)
        # s3_object.put(
        #     Body=(bytes(json.dumps(data).encode('UTF-8')))
        # )
        with open(f'{os.getcwd()}/{storing_key}', "w", encoding = 'UTF-8') as outfile:
            outfile.write(json.dumps(data, indent = 6))
        self._logger.info('Written to s3 with key %s', storing_key)
        return True
    
    # def insert_into_collection(self, collection_name: str, **kwargs):
    #     """
    #     Store json data into the MongoDB database

    #     :param collection_name: Name of collection where the data is to be stored
    #     """
    #     collection  = self._db[collection_name]
    #     data = {key: value for key, value in kwargs.items()}
    #     collection.insert_one(data)
    #     return True
