import subprocess
import threading
from disco import Events

def playSongAndWait(discoMachine):
    audioProcess = subprocess.Popen(['aplay', 'disco.wav',])
    result = audioProcess.wait()
    discoMachine.addEvent(Events.SongStopped)

class Tapedeck:
    def __init__(self,discoMachine):
        self.machine = discoMachine
        None

    def start(self):
        thread = threading.Thread(target=playSongAndWait,args=(self.machine,))
        thread.run()


        