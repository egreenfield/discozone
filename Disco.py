

import RPi.GPIO as GPIO
import time
import subprocess
import datetime
import os
from threading import Thread
from dataclasses import dataclass

# config
DISTANCE_IN_CM = 60
MOTOR_SPEED = .6

from enum import Enum
class DiscoState(Enum):
    LOOKING = 1
    CLEARING = 2
    PLAYING = 3

motoRPin1 = 13
motoRPin2 = 11
enablePin = 15
#adc = ADCDevice() # Define an ADCDevice class object


@dataclass
class DiscoFeatures:
    ball:bool = True
    music:bool = True
    video:bool = True    



def mapNUM(value,fromLow,fromHigh,toLow,toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

class Disco:
    state:DiscoState = DiscoState.CLEARING
    audioProcess: subprocess.Popen = None
    currentVideoName: str = ""
    videoProcess: subprocess.Popen = None
    p = None

    def __init__(self,features):
        self.features = features

    def setup(self):
        self.setupMotor()

    def setupMotor(self):
        GPIO.setmode(GPIO.BOARD)   
        GPIO.setup(motoRPin1,GPIO.OUT)   # set pins to OUTPUT mode
        GPIO.setup(motoRPin2,GPIO.OUT)
        GPIO.setup(enablePin,GPIO.OUT)

        self.p = GPIO.PWM(enablePin,1000) # creat PWM and set Frequence to 1KHz
        self.p.start(0)

    # motor function: determine the direction and speed of the motor according to the input ADC value input
    def motor(self,ADC):
        value = ADC -128
        if (value > 0):  # make motor turn forward
            GPIO.output(motoRPin1,GPIO.HIGH)  # motoRPin1 output HIHG level
            GPIO.output(motoRPin2,GPIO.LOW)   # motoRPin2 output LOW level
        elif (value < 0): # make motor turn backward
            GPIO.output(motoRPin1,GPIO.LOW)
            GPIO.output(motoRPin2,GPIO.HIGH)
        else :
            GPIO.output(motoRPin1,GPIO.LOW)
            GPIO.output(motoRPin2,GPIO.LOW)
        self.p.start(mapNUM(abs(value),0,128,0,100))
    #    print ('The PWM duty cycle is %d%%\n'%(abs(value)*100/127))   # print PMW duty cycle.

    def destroyMotor(self):
        self.p.stop()  # stop PWM


    def startVideo(self):
        if(self.features.video == False):
            return
        now = datetime.datetime.now()
        self.currentVideoName = f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}'
        print(f'video name is {self.currentVideoName}')
        self.videoProcess = subprocess.Popen(['raspivid', '-o', f'{self.currentVideoName}.h264', '-t', '30000'])

    def stopVideo(self):
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

    def foundSomeone(self):
        if(self.state != DiscoState.LOOKING):
            return

        self.state = DiscoState.PLAYING
        self.motor(128 + 128 * MOTOR_SPEED)
        self.audioProcess = subprocess.Popen(['cvlc', 'disco.m4a', 'vlc://quit'])
        time.sleep(4)
        self.startVideo()

    def stopPlaying(self):    
        self.state = DiscoState.CLEARING
        self.audioProcess = None
        self.motor(128)
        self.stopVideo()

    def startLooking(self):
        self.state = DiscoState.LOOKING

    def checkForEndOfSong(self):
        if(self.state != DiscoState.PLAYING):
            return
        if(self.audioProcess == None):
            self.stopPlaying();
        else:
            result = self.audioProcess.poll();
            if (result != None):
                self.stopPlaying();

    def waitForClear(self):
        if(self.state != DiscoState.CLEARING):
            return
        self.startLooking()

    def shutdown(self):
        self.destroyMotor()
    
    def pump(self):
        self.checkForEndOfSong();
        self.waitForClear()
