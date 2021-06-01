import subprocess
import datetime
import os
import re
from collections import deque
import threading
import devices
from twilio.rest import Client
from remote_storage import S3Storage

import logging
log = logging.getLogger(__name__)

class PackagerThread (threading.Thread):
    videos = deque()
    lock = threading.Condition()

    def __init__(self,recorder):
        threading.Thread.__init__(self,daemon=True)
        self.recorder = recorder
        self.completedVideos = deque()

    def run(self):
#        self.findOldJobs()
        while(True):
            videoName = None
            with self.lock:
                while not len(self.videos):
                    self.lock.wait()
                (videoName,danceID) = self.videos.popleft()
                log.debug(f'packaging {videoName}')                
            self._package(videoName,danceID)

    def h264Name(filename):
        m = re.search(r"(.*)\.h264",filename)
        if(m == None):
            return False;
        return m.group(1)

    def findOldJobs(self):
        files = os.listdir(self.recorder.localStorage)
        files = map(lambda videoName : videoName.split(".")[0], filter(lambda videoName : re.search(r"(.*)\.h264",videoName) != None,files))
        log.debug(f'found {files} waiting to be processed')
        for aFile in files:
            self.videos.append(aFile)

    def _package(self,videoName,danceID):
        videoRemoved = False
        videoPath = os.path.join(self.recorder.localStorage,videoName)
        h264Path = f'{videoPath}.h264'
        mp4Path =  f'{videoPath}.mp4'
        boxProc = subprocess.Popen(['MP4Box', '-add', h264Path, mp4Path])
        boxProc.wait()
        if os.path.exists(h264Path):
            os.remove(h264Path)             
        if (self.recorder.remoteStorage):
            remoteVideoFilename = "videos/"+ os.path.basename(mp4Path)
            uploaded = self.recorder.remoteStorage.upload(mp4Path,remoteVideoFilename)
            if(uploaded == True and self.recorder.deleteOnUpload):
                os.remove(mp4Name)             
                videoRemoved = True
        self.recorder.danceClient.registerDanceVideo(danceID,remoteVideoFilename)
        
        if(videoRemoved):
            return
        self.completedVideos.append(mp4Path)
        if(self.recorder.maxVideoCount > 0 and len(self.completedVideos) > self.recorder.maxVideoCount):
            deadVideo = self.completedVideos.popleft()
            os.remove(deadVideo)

        if(self.recorder.sendSMS):
            self.sendNotification(f'{videoName}.mp4')

    def sendNotification(self,videoFilename):
        account_sid = self.recorder.twilioId
        auth_token = self.recorder.twilioToken
        client = Client(account_sid, auth_token)

        message = client.messages \
                        .create(
                            body=f'Disco Stu has a new convert.  See it here:  http://disco-videos.s3-website-us-west-2.amazonaws.com/{videoFilename}',
                            from_=self.recorder.smsFrom,
                            to=self.recorder.smsTo
                        )

    
    def package(self,videoName,danceID):
        with(self.lock):
            self.videos.append((videoName,danceID))
            self.lock.notify()

class VideoRecorderCommand:
    START = "Videorecorder:start"
    STOP = "Videorecorder:stop"

class VideoRecorderEventProperties:
    DANCE_ID = "danceID"
class VideoRecorder(devices.Device):
    currentVideoName:str = None
    currentDanceID:str = None
    videoProcess:subprocess.Popen = None
    deleteOnUpload:bool = True
    maxVideoCount:int = 0
    localStorage:str = ""
    flip = True
    sendSMS = False
    smsFrom = ""
    smsTo = ""
    twilioId = ""
    twilioToken = ""

    def __init__(self,app):
        devices.Device.__init__(self,app)
        self.remoteStorage = None
        self.danceClient = app.danceClient

    def setConfig(self,config,globalConfig):
        devices.Device.setConfig(self,config,globalConfig)
        if('localStorage' in config):
            self.localStorage = config['localStorage']
        if('deleteOnUpload' in config):
            self.deleteOnUpload = config['deleteOnUpload']
        if('maxVideoCount' in config):
            self.maxVideoCount = config['maxVideoCount']
        if('flip' in config):
            self.flip = config['flip']
        if('sendSMS' in config):
            self.sendSMS = config['sendSMS']
            if(self.sendSMS):
                self.twilioId = config['twilioId']
                self.twilioToken = config['twilioToken']
                if('smsFrom' in config):
                    self.smsFrom = config['smsFrom']
                if('smsTo' in config):
                    self.smsTo = config['smsTo']
        if('storageOptions' in config):
            self.remoteStorage = S3Storage()
            self.remoteStorage.setConfig(config['storageOptions'])

    def init(self):
        self.packager = PackagerThread(self)
        self.packager.start()

    def onCommand(self,cmd,data):
        if(cmd == VideoRecorderCommand.START):
            danceID = data[VideoRecorderEventProperties.DANCE_ID]
            self.start(danceID)
        elif(cmd == VideoRecorderCommand.STOP):
            self.stop()


    def start(self,danceID):
        now = datetime.datetime.now()
        self.currentVideoName =  now.strftime("%Y_%m_%d_%H_%M_%S")
        self.currentDanceID = danceID
        log.info(f'video name is {self.currentVideoName}')
        if(self.flip):
            opts = ['raspivid', '--vflip','--hflip','-o', f'{os.path.join(self.localStorage,self.currentVideoName)}.h264', '-t', '30000']
        else:
            opts = ['raspivid', '-o', f'{os.path.join(self.localStorage,self.currentVideoName)}.h264', '-t', '30000']
        self.videoProcess = subprocess.Popen(opts)

    def stop(self):
        if(self.videoProcess != None):
            self.videoProcess.terminate()
            self.videoProcess = None
            self.packager.package(self.currentVideoName,self.currentDanceID)
            self.currentVideoName = None
