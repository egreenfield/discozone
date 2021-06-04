import RPi.GPIO as GPIO
import time
import subprocess
import threading
from disco import Events
import devices
from enum import Enum

import logging
log = logging.getLogger(__name__)
from datetime import datetime, timedelta

DEFAULT_TRIGGER_PIN = 16
DEFAULT_ECHO_PIN = 18
DEFAULT_MAX_SENSOR_RANGE = 220          # define the maximum measuring distance, unit: cm
DEFAULT_DETECTION_DISTANCE_IN_CM = 60
MINIMUM_DETECTION_DISTANCE = 5
DEFAULT_DEBOUNCE_RATE = 3

class SonarEvent:
    PERSON_APPROACHING = "Sonar:PersonApproaching"
    PERSON_LEFT = "Sonar:PersonLeft"

class SonarState(Enum):
    ObjectDetected = "SonarState:ObjectDetected"
    Clear = "SonarState:Clear"

class SonarCommand:
    LOG = "SonarCommand:log"

class WatchingThread (threading.Thread):

    def __init__(self,device):
        threading.Thread.__init__(self,daemon=True)
        self.lastSeenState = None
        self.seenCount = 0
        self.sampleJournal = []        
        self.device = device
        self.terminated = False
        self.journalLock = threading.RLock()

    def pulseIn(self,pin,level,timeOut): # obtain pulse time of a pin under timeOut
        t0 = time.time()
        while(GPIO.input(pin) != level):
            if((time.time() - t0) > timeOut*0.000001):
                return 0;
        t0 = time.time()
        while(GPIO.input(pin) == level):
            if((time.time() - t0) > timeOut*0.000001):
                return 0;
        pulseTime = (time.time() - t0)*1000000
        return pulseTime

    def readSensor(self):     # get the measurement results of ultrasonic module,with unit: cm
        GPIO.output(self.device.triggerPin,GPIO.HIGH)      # make trigPin output 10us HIGH level 
        time.sleep(0.00001)     # 10us
        GPIO.output(self.device.triggerPin,GPIO.LOW) # make trigPin output LOW level 
        timeOut = self.device.maxSensorRange*60   # calculate timeout according to the maximum measuring distance
        pingTime = self.pulseIn(self.device.echoPin,GPIO.HIGH,timeOut)   # read plus time of echoPin
        distance = pingTime * 340.0 / 2.0 / 10000.0     # calculate distance with sound speed 340m/s 
        return distance

    def journalDistance(self,distance):
        with self.journalLock:
            # if(distance < 100):
            # print(f'LOOKING: d: {int(distance)}, min:{self.device.minimumDistance} max:{self.device.detectionDistance}')
            now = datetime.utcnow()
            self.sampleJournal.append({
                "time": now,
                "distance": distance
            })        
            maxDelta = timedelta(seconds=3)
            while len(self.sampleJournal) > 0:
                delta = now - self.sampleJournal[0]['time']
                if (delta > maxDelta):
                    self.sampleJournal.pop(0)
                else:
                    break            

    def checkReport(self):
        pass

    def checkForChange(self):
        distance = self.readSensor() # get distance

        self.journalDistance(distance)

        if (distance < self.device.minimumDistance and distance > 0):
            return
        if (distance < self.device.detectionDistance and distance > 0):
            foundState = SonarState.ObjectDetected
        else:
            foundState = SonarState.Clear
        if(foundState != self.lastSeenState):
            self.lastSeenState = foundState
            self.seenCount = 0
        self.seenCount += 1
        #print(f'foundState:{foundState},seenCount:{self.seenCount},distaince:{distance}')
        if(self.seenCount < self.device.debounceRate):        
            return
        if (foundState == SonarState.ObjectDetected):
            if(self.device.state == SonarState.Clear):
                print(f'-------------------- SONAR found object {distance}')
                self.device.state = SonarState.ObjectDetected
                self.device.raiseEvent(SonarEvent.PERSON_APPROACHING)
        else:
            if(self.device.state == SonarState.ObjectDetected):
                #print(f'SONAR cleared object {distance}')
                self.device.state = SonarState.Clear
                self.device.raiseEvent(SonarEvent.PERSON_LEFT)            


    def run(self):
        t0 = time.time()
        pingCount = 0
        while not (self.terminated):
            self.checkForChange()
#            pingCount += 1
            time.sleep(.1) 
#            t1 = time.time()
#            if(t1 - t0 > 5):
#                print(f' got {pingCount} pings in {t1-t0} seconds, (or {pingCount/(t1-t0)}/sec')
#                pingCount = 0
#                t0 = t1







class Sonar(devices.Device):
    

    def __init__(self,app):
        devices.Device.__init__(self,app)
        self.danceClient = app.danceClient
        self.detectionDistance = DEFAULT_DETECTION_DISTANCE_IN_CM
        self.minimumDistance = MINIMUM_DETECTION_DISTANCE
        self.triggerPin = DEFAULT_TRIGGER_PIN
        self.echoPin = DEFAULT_ECHO_PIN
        self.maxSensorRange = DEFAULT_MAX_SENSOR_RANGE
        self.state = SonarState.Clear
        self.debounceRate = DEFAULT_DEBOUNCE_RATE

    def init(self):
        GPIO.setmode(GPIO.BOARD)      # use PHYSICAL GPIO Numbering
        GPIO.setup(self.triggerPin, GPIO.OUT)   # set trigPin to OUTPUT mode
        GPIO.setup(self.echoPin, GPIO.IN)    # set echoPin to INPUT mode

        self.watcher = WatchingThread(self)
        self.watcher.start()

    def setConfig(self,config,globalConfig):
        devices.Device.setConfig(self,config,globalConfig)
        if('detectionDistance' in config):
            self.detectionDistance = config['detectionDistance']
        if('minimumDistance' in config):
            self.minimumDistance = config['minimumDistance']
        if('triggerPin' in config):
            self.triggerPin = config['triggerPin']
        if('echoPin' in config):
            self.echoPin = config['echoPin']
        if('maxSensorRange' in config):
            self.maxSensorRange = config['maxSensorRange']
        if('debounceRate' in config):
            self.debounceRate = config['debounceRate']
        self.journalLength = config.get('journalLength',3)
        self.journalDelay = config.get('journalDelay',.5)

    def shutdown(self):
        self.watcher.terminated = True
        self.watcher.join()

    def log(self,danceID):
        with self.watcher.journalLock:
            self.danceClient.logSonarSamples(danceID,{
                "version": 1,
                "source": self.id,
                "samples": self.watcher.sampleJournal
            })
        pass


    def startLog(self,data):
        threading.Timer(self.journalDelay, lambda : self.log(data['id'])).start()

    def onCommand(self,cmd,data):
        if (cmd == SonarCommand.LOG):
            self.startLog(data)
