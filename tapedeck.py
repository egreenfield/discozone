import subprocess
import threading
import os
import time
from disco import Events
import devices


class TapedeckCommand:
    PLAY = "Tapedeck:start"
    STOP = "Tapedeck:stop"

class TapedeckEvent:
    SONG_STOPPED = "Tapedeck:songStopped"
    STOP = "Tapedeck:stop"

class PlaybackThread (threading.Thread):
    
    _abort = False
    
    def __init__(self,tapedeck,song):
        threading.Thread.__init__(self)
        self.tapedeck = tapedeck
        self.song = song

    def run(self):
        audioProcess = subprocess.Popen(['aplay', self.song])
        while(True):
            if (self._abort):
                audioProcess.terminate()
                break
            elif (audioProcess.poll() != None):
                self.tapedeck.raiseEvent(TapedeckEvent.SONG_STOPPED)
                break
            else:
                time.sleep(.2)
        
    def abort(self):
        self._abort = True


class Tapedeck(devices.Device):
    def __init__(self,app):
        devices.Device.__init__(self,app)
        self.thread = None
        self.fileIndex = 0


    def onCommand(self,cmd,data = None):
        if(cmd == TapedeckCommand.PLAY):
            self.start(data['song'])
        elif(cmd == TapedeckCommand.STOP):
            self.stop()

    def start(self,song):
        if(self.thread):
            self.thread.abort()
        self.thread = PlaybackThread(self,song)
        self.thread.start()

    def stop(self):
        if(self.thread):
            self.thread.abort()


        