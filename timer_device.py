import threading
import devices

class TimerEvent:
    TIMER_COMPLETE = "Timer:Complete"

class TimerCommand:
    START = "Timer:start"

class TimerDevice(devices.Device):

    def __init__(self):
        devices.Device.__init__(self)
        self.duration = 10

    def setConfig(self,config,globalConfig):
        devices.Device.setConfig(self,config,globalConfig)
        if('duration' in config):
            self.duration = config['duration']


    def start(self):
        threading.Timer(self.duration, lambda : self.trigger()).start()

    def trigger(self):
        self.raiseEvent(TimerEvent.TIMER_COMPLETE)

    def onCommand(self,cmd,data = None):
        if(cmd == TimerCommand.START):
            self.start()
