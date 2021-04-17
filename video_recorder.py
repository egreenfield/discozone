import subprocess
import datetime
import os

class VideoRecorder:
    currentVideoName:str = None
    videoProcess:subprocess.Popen = None

    def __init__(self):
        None


    def start(self):
        now = datetime.datetime.now()
        self.currentVideoName = f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}'
        print(f'video name is {self.currentVideoName}')
        self.videoProcess = subprocess.Popen(['raspivid', '-o', f'{self.currentVideoName}.h264', '-t', '30000'])

    def finish(self):
        if(self.features.video == False):
            return
        if(self.videoProcess != None):
            h264Name = f'{self.currentVideoName}.h264'
            self.videoProcess.terminate()
            self.videoProcess = None
            boxProc = subprocess.Popen(['MP4Box', '-add', h264Name, f'{self.currentVideoName}.mp4'])
            boxProc.wait()
            if os.path.exists(h264Name):
                os.remove(h264Name)
            self.currentVideoName = ''
