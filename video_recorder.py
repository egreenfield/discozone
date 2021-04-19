import subprocess
import datetime
import os
from collections import deque
import threading
import devices
from enum import Enum

import logging
log = logging.getLogger(__name__)

class PackagerThread (threading.Thread):
    videos = deque()
    lock = threading.Condition()

    def __init__(self,destination):
        threading.Thread.__init__(self,daemon=True)
        self.fileStorage = destination

    def run(self):
        while(True):
            videoName = None
            with self.lock:
                while not len(self.videos):
                    self.lock.wait()
                videoName = self.videos.popleft()
                log.debug(f'packaging {videoName}')
                

            h264Name = f'{videoName}.h264'
            mp4Name =  f'{videoName}.mp4'
            boxProc = subprocess.Popen(['MP4Box', '-add', h264Name, mp4Name])
            boxProc.wait()
            if os.path.exists(h264Name):
                os.remove(h264Name)             
            if(self.fileStorage):
                scpProc = subprocess.Popen(['scp', mp4Name, self.fileStorage])
                scpProc.wait()
            
    
    def addVideo(self,videoName):
        with(self.lock):
            self.videos.append(videoName)
            self.lock.notify()

class VideoRecorderCommand(Enum):
    START = "Videorecorder:start"
    STOP = "Videorecorder:stop"

class VideoRecorder(devices.Device):
    currentVideoName:str = None
    videoProcess:subprocess.Popen = None
    remoteStorage:str = None

    
    def __init__(self):
        devices.Device.__init__(self)

    def setConfig(self,config):
        self.remoteStorage = config['remoteStorage']

    def init(self):
        self.packager = PackagerThread(self.remoteStorage)
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
        self.videoProcess = subprocess.Popen(['raspivid', '-o', f'{self.currentVideoName}.h264', '-t', '30000'])

    def stop(self):
        if(self.videoProcess != None):
            self.videoProcess.terminate()
            self.videoProcess = None
            self.packager.addVideo(self.currentVideoName)
            self.currentVideoName = None
