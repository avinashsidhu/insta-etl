"""
Running the application
"""
from source.connector import Connector
from source.pipeline import InstagramPipeline

def main():
    """
    Entry point to run the application
    """
    connection = Connector('API_KEY')
    pipeline = InstagramPipeline(connection)
    print(pipeline.extract_user_profile(123))

if __name__ == '__main__':
    main()
