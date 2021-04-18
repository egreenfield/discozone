import subprocess
import threading
import time
from disco import Events

def playSongAndWait(discoMachine):
    audioProcess = subprocess.Popen(['aplay', 'disco.wav',])
    result = audioProcess.wait()
    discoMachine.addEvent(Events.SongStopped)

class PlaybackThread (threading.Thread):
    
    _abort = False
    
    def __init__(self,machine):
        threading.Thread.__init__(self)
        self.machine = machine

    def run(self):
        audioProcess = subprocess.Popen(['aplay', 'disco.wav',])
        while(True):
            if (self._abort):
                audioProcess.terminate()
                break
            elif (audioProcess.poll() != None):
                self.machine.addEvent(Events.SongStopped)
                break
            else:
                time.sleep(.2)
        
    def abort(self):
        self._abort = True

class Tapedeck:
    def __init__(self,machine):
        self.machine = machine
        self.thread = None

    def start(self):
        if(self.thread):
            self.thread.abort()
        self.thread = PlaybackThread(self.machine)
        self.thread.start()

    def stop(self):
        if(self.thread):
            self.thread.abort()


        