import logging
import json
import boto3
import botocore
from functools import reduce

logger = logging.getLogger()
logger.setLevel(logging.INFO)




def extract(objects,dance):
    videoFile = dance['videofile']
    sonarFile = f'sonar/{dance["id"]}'
    if(len(videoFile) > 0):
        objects.append(videoFile)
    objects.append(sonarFile)
    return objects
    
class DiscoFilebase:
    def __init__(self,resourceBucket):
        botoConfig = botocore.config.Config(s3={'addressing_style':'path'})
        self.s3client = boto3.client('s3')
        self.resourceBucket = resourceBucket
        logger.info(f's3 is {self.s3client}, delete is {self.s3client.delete_objects}')

    def deleteDanceFiles(self,dances):

        logger.info(f'dances passed in are json.dumps{dances}')
        objectNames = reduce(extract,dances,[])

        deleteOptions = {
            'Quiet':False,
            'Objects': list(map(lambda objectName: {'Key':objectName},objectNames))
        }
        self.s3client.delete_objects(Bucket=self.resourceBucket,Delete=deleteOptions)
        return 0
