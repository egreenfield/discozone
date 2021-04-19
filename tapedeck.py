import subprocess
import threading
import time
from disco import Events
import devices
from enum import Enum


class TapedeckCommand(Enum):
    START = "Tapedeck:start"
    STOP = "Tapedeck:stop"

class TapedeckEvent:
    SONG_STOPPED = "Tapedeck:songStopped"
    STOP = "Tapedeck:stop"

class PlaybackThread (threading.Thread):
    
    _abort = False
    
    def __init__(self,tapedeck):
        threading.Thread.__init__(self)
        self.tapedeck = tapedeck

    def run(self):
        audioProcess = subprocess.Popen(['aplay', 'disco.wav',])
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
    def __init__(self):
        devices.Device.__init__(self)
        self.thread = None

    def onCommand(self,cmd,data = None):
        if(cmd == TapedeckCommand.START):
            self.start()
        elif(cmd == TapedeckCommand.STOP):
            self.stop()

    def start(self):
        if(self.thread):
            self.thread.abort()
        self.thread = PlaybackThread(self)
        self.thread.start()

    def stop(self):
        if(self.thread):
            self.thread.abort()


        