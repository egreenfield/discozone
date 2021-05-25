import boto3
from botocore.config import Config

bucketName = "disco-videos"

myConfig = Config(
    region_name = 'us-west-2',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

s3 = boto3.resource('s3')

bucket = s3.Bucket(bucketName)
print("bucket contents:")
for object in bucket.objects.all():
    print(object.key)
