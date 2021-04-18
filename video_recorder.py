import subprocess
import datetime
import os
from collections import deque
import threading

import logging
log = logging.getLogger(__name__)

class PackagerThread (threading.Thread):
    videos = deque()
    lock = threading.Condition()

    def __init__(self):
        threading.Thread.__init__(self,daemon=True)

    def run(self):
        while(True):
            videoName = None
            with self.lock:
                while not len(self.videos):
                    log.debug(f'waiting to package')
                    self.lock.wait()
                videoName = self.videos.popleft()
                log.debug(f'packaging {videoName}')
                

            h264Name = f'{videoName}.h264'
            boxProc = subprocess.Popen(['MP4Box', '-add', h264Name, f'{videoName}.mp4'])
            boxProc.wait()
            if os.path.exists(h264Name):
                os.remove(h264Name)             
    
    def addVideo(self,videoName):
        with(self.lock):
            self.videos.append(videoName)
            self.lock.notify()


class VideoRecorder:
    currentVideoName:str = None
    videoProcess:subprocess.Popen = None

    def __init__(self):
        self.packager = PackagerThread()
        self.packager.start()


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
