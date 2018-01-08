
import boto3

from scrapy.extensions.feedexport import BlockingFeedStorage

AWS_PROFILE = 'koodivelho'
BUCKET_NAME = 'testaus-bucket'
KEY_NAME = 'hy_courses.json'

class CourseS3FeedStorage(BlockingFeedStorage):
    def __init__(self, uri):
        session = boto3.Session(profile_name=AWS_PROFILE)
        self.s3_client = session.client('s3')

    def _store_in_thread(self, file):
        file.seek(0)
        self.s3_client.put_object(Bucket=BUCKET_NAME, Key=KEY_NAME, Body=file)