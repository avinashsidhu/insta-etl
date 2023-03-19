"""
Running the application
"""
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
    args = parser.parse_args()
    config = yaml.safe_load(open(args.config, 'rt', encoding='utf8'))
    log_config = config['logging']
    logging.config.dictConfig(log_config)

    logger = logging.getLogger(__name__)
    logger.info('Job started.')
    source_api = SourceConnector('API_KEY')
    destination_db = DestinationConnector()
    pipeline = InstagramPipeline(source_api, destination_db)
    pipeline.ETL_per_user(123, datetime.strptime("2023-1-1", "%Y-%m-%d"))
    logger.info('Job finished.')


if __name__ == '__main__':
    main()
