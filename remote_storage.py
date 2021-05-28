import boto3
from botocore.config import Config
import os

import logging
log = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        self.bucketName = ""
        self.accessKey = ""
        self.secretKey = ""
        self.client = None

    def setConfig(self,config):
        if('bucketName' in config):
            self.bucketName = config['bucketName']
        if('accessKey' in config):
            self.accessKey = config['accessKey']
        if('secretKey' in config):
            self.accessKey = config['secretKey']

    def createClient(self):
        myConfig = Config(
            region_name = 'us-west-2',
        )
        self.client = boto3.client('s3', config=myConfig)

    def upload(self,filename,remoteName=None):
        if(self.client == None):
            self.createClient()
        try:
            objectName = remoteName
            if(objectName == None):
                objectName = os.path.basename(filename)
            self.client.upload_file(filename, self.bucketName, objectName,ExtraArgs={'ContentType': 'video/mp4'})
            return True
        except FileNotFoundError:
            log.debug("Upload failed: local file not found")
            return False
        except NoCredentialsError:
            log.debug("Upload failed: S3 Credentials invalid")
            return False

