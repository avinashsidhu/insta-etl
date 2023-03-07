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
    user_id = 123
    print(pipeline.extract_user_profile(user_id))

if __name__ == '__main__':
    main()
