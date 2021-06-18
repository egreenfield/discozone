import boto3
from botocore.config import Config
import os
import json
import datetime
import threading
from collections import deque


import logging
log = logging.getLogger(__name__)

def convertDates(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def toJson(o):
    return json.dumps(o, default = convertDates)

class S3BackgroundUploader (threading.Thread):
    def __init__(self,storage):
        threading.Thread.__init__(self,daemon=True)
        self.storage = storage
        self.uploads = deque()
        self.lock = threading.Condition()

    def run(self):
        # TODO need to put a lock around the client to prevent background and foreground use
        while(True):
            objectName = None
            with self.lock:
                while not len(self.uploads):
                    self.lock.wait()
                (objectName,body) = self.uploads.popleft()
                log.debug(f'uploading {objectName}')
            self.upload(objectName,body)

    def upload(self,objectName,body):
        client = self.storage.client
        client.put_object(Bucket=self.storage.bucketName,
                            Key=objectName,
                            Body=(bytes(body.encode('UTF-8'))),
                            ContentType='application/json'
        )
        return True

    def queueUpload(self,objectName,body):
        with self.lock:
            self.uploads.append((objectName,body))
            self.lock.notify()


class S3Storage:
    def __init__(self):
        self.client = None
        self.uploader = S3BackgroundUploader(self)
        self.uploader.start()

    def setConfig(self,config):
            self.bucketName = config.get('bucketName',None)
            if (self.bucketName):
                self.createClient()

    def createClient(self):
        myConfig = Config(
            region_name = 'us-west-2',
        )
        self.client = boto3.client('s3', config=myConfig)

    def upload(self,filename,remoteName=None):
        return self.uploadSync(filename,remoteName)

    def listObjects(self,prefix = ""):
        # s3 = boto3.resource('s3')

        # bucket = s3.Bucket(self.bucketName)
        # return list(bucket.objects.filter(Prefix=prefix))
        response = self.client.list_objects_v2(Bucket=self.bucketName,Prefix=prefix)
        return response['Contents']

    def uploadSync(self,filename,remoteName=None):

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

    def uploadObject(self,remoteName,data):
        self.uploadObjectAsync(remoteName,data)

    def uploadObjectAsync(self,remoteName,data):
        body = toJson(data)
        self.uploader.queueUpload(remoteName,body)
