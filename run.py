"""
Running the application
"""
import argparse
import logging
import logging.config
from datetime import datetime
import yaml
from source.connector import Connector
from source.pipeline import InstagramPipeline

def main():
    """
    Entry point to run the application
    """
    parser = argparse.ArgumentParser(description='Run the Job.')
    parser.add_argument('config', help='A configuration file in YAML format.')
    args = parser.parse_args()
    config = yaml.safe_load(open(args.config, 'rt', encoding='utf8'))
    log_config = config['logging']
    logging.config.dictConfig(log_config)

    logger = logging.getLogger(__name__)
    logger.info('Job started.')
    connection = Connector('API_KEY')
    pipeline = InstagramPipeline(connection)
    user_id = 5465455115
    profile_info, followers, following, postids, post_infos, likes, comments = pipeline.extract_per_user(
        user_id, datetime.strptime("2023-1-1", "%Y-%m-%d"))

    print(profile_info)
    print(len(followers))
    print(len(following))
    print(len(postids))
    print(post_infos)
    for postid, like in zip(postids, likes):
        print(postid, len(like))
    for postid, comment in zip(postids, comments):
        print(postid, len(comment))

    logger.info('Job finished.')


if __name__ == '__main__':
    main()
