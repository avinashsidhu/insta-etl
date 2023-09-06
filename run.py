"""
Running the application
"""
import os
import argparse
import logging
import logging.config
from datetime import datetime
import yaml
from source.connector import SourceConnector, DestinationConnector
from source.pipeline import InstagramPipeline

def main():
    """
    Entry point to run the application
    """
    parser = argparse.ArgumentParser(description='Run the Job.')
    parser.add_argument('config', help='A configuration file in YAML format.')
    # args = parser.parse_args()
    # config = yaml.safe_load(open(args.config, 'rt', encoding='utf8'))
    config_path = f'{os.getcwd()}/configs/config.yml'
    config = yaml.safe_load(open(config_path, 'rt', encoding='utf8'))
    log_config = config['logging']
    run_config = config['run']
    s3_config = config['s3']
    logging.config.dictConfig(log_config)

    logger = logging.getLogger(__name__)
    logger.info('Job started.')

    source_api = SourceConnector('API_KEY')
    destination_db = DestinationConnector(access_key=s3_config['access_key'],
                                      secret_key=s3_config['secret_key'],
                                      endpoint_url=s3_config['endpoint_url'],
                                      bucket=s3_config['bucket'])

    if run_config['type'] == 'POSTS':
        logger.info('Fetching post info')
        pipeline = InstagramPipeline(source_api, destination_db)
        path_to_shortcodes = run_config['path']
        column_name = run_config['column_name']
        pipeline.ETL_posts(path_to_shortcodes, column_name)
    elif run_config['type'] == 'USERS':
        logger.info('Fetching user info.')
        pipeline = InstagramPipeline(source_api, destination_db)
        path_to_user_ids = run_config['path']
        time_to_process_from = run_config['time']
        time_format = run_config['time_format']
        column_name = run_config['column_name']
        pipeline.ETL_users(path_to_user_ids, column_name, time_to_process_from, time_format)
    else:
        logger.info('Please provide correct run type.')
    logger.info('Job finished.')
    logging.shutdown()

if __name__ == '__main__':
    main()
