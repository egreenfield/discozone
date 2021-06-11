import logging
import json
import boto3
import botocore
from functools import reduce

logger = logging.getLogger()
logger.setLevel(logging.INFO)




def extract(objects,dance):
    objects.append(dance['videofile'])
    objects.append(f'sonar/{dance["id"]}')
    return objects
    
class DiscoFilebase:
    def __init__(self,resourceBucket):
        botoConfig = botocore.config.Config(s3={'addressing_style':'path'})
        self.s3client = boto3.client('s3',config=botoConfig)
        self.resourceBucket = resourceBucket

    def deleteDanceFiles(self,dances):

        logger.info(f'dances passed in are json.dumps{dances}')
        objectNames = reduce(extract,dances,[])

        deleteOptions = {
            'Quiet':True,
            'Objects': list(map(lambda objectName: {'Key':objectName},objectNames))
        }
        return {
            "Bucket":self.resourceBucket,
            "Delete":deleteOptions
        }
        # response = client.delete_objects(Bucket=resourceBucket,
        # Delete=deleteOptions)