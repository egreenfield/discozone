import subprocess
import datetime
import os
from collections import deque
import threading
import devices

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
        while(True):
            videoName = None
            with self.lock:
                while not len(self.videos):
                    self.lock.wait()
                videoName = self.videos.popleft()
                log.debug(f'packaging {videoName}')                
            self._package(videoName)

    def _package(self,videoName):
        videoRemoved = False
        videoPath = os.path.join(self.recorder.localStorage,videoName)
        h264Path = f'{videoPath}.h264'
        mp4Path =  f'{videoPath}.mp4'
        boxProc = subprocess.Popen(['MP4Box', '-add', h264Path, mp4Path])
        boxProc.wait()
        if os.path.exists(h264Path):
            os.remove(h264Path)             
        if (self.recorder.remoteStorage):
            scpProc = subprocess.Popen(['scp', mp4Path, self.recorder.remoteStorage])
            result = scpProc.wait()
            print(f'upload result is {result}')
            if(result == 0 and self.recorder.deleteOnUpload):
                os.remove(mp4Name)             
                videoRemoved = True
        if(videoRemoved):
            return
        self.completedVideos.append(mp4Path)
        if(len(self.completedVideos) > self.recorder.maxVideoCount):
            deadVideo = self.completedVideos.popleft()
            os.remove(deadVideo)

    
    def package(self,videoName):
        with(self.lock):
            self.videos.append(videoName)
            self.lock.notify()

class VideoRecorderCommand:
    START = "Videorecorder:start"
    STOP = "Videorecorder:stop"

class VideoRecorder(devices.Device):
    currentVideoName:str = None
    videoProcess:subprocess.Popen = None
    remoteStorage:str = None
    deleteOnUpload:bool = True
    maxVideoCount:int = 20
    localStorage:str = ""
    flip = True

    def __init__(self):
        devices.Device.__init__(self)

    def setConfig(self,config):
        devices.Device.setConfig(self,config)
        if('remoteStorage' in config):
            self.remoteStorage = config['remoteStorage']
        if('localStorage' in config):
            self.localStorage = config['localStorage']
        if('deleteOnUpload' in config):
            self.deleteOnUpload = config['deleteOnUpload']
        if('maxVideoCount' in config):
            self.maxVideoCount = config['maxVideoCount']
        if('flip' in config):
            self.flip = config['flip']

    def init(self):
        self.packager = PackagerThread(self)
        self.packager.start()

    def onCommand(self,cmd,data = None):
        if(cmd == VideoRecorderCommand.START):
            self.start()
        elif(cmd == VideoRecorderCommand.STOP):
            self.stop()


    def start(self):
        now = datetime.datetime.now()
        self.currentVideoName = f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}'
        print(f'video name is {self.currentVideoName}')
        if(self.flip):
            opts = ['raspivid', '--vflip','--hflip','-o', f'{os.path.join(self.localStorage,self.currentVideoName)}.h264', '-t', '30000']
        else:
            ops = ['raspivid', '-o', f'{os.path.join(self.localStorage,self.currentVideoName)}.h264', '-t', '30000']
        self.videoProcess = subprocess.Popen(opts)

    def stop(self):
        if(self.videoProcess != None):
            self.videoProcess.terminate()
            self.videoProcess = None
            self.packager.package(self.currentVideoName)
            self.currentVideoName = None
