#!/usr/bin/env python3
########################################################################
# Filename    : UltrasonicRanging.py
# Description : Get distance via UltrasonicRanging sensor
# auther      : www.freenove.com
# modification: 2019/12/28
########################################################################
import RPi.GPIO as GPIO
import time
import subprocess
import datetime
import os

# config
DISTANCE_IN_CM = 60
MOTOR_SPEED = .6

from enum import Enum
class State(Enum):
    LOOKING = 1
    CLEARING = 2
    PLAYING = 3


# define the pins connected to L293D 
motoRPin1 = 13
motoRPin2 = 11
enablePin = 15
#adc = ADCDevice() # Define an ADCDevice class object
process = None

from dataclasses import dataclass


@dataclass
class AppState:
    state: State
    process: subprocess.Popen
    currentVideoName: str = ""
    videoProcess: subprocess.Popen = None

state = State.LOOKING


def setupMotor():
    global p
    GPIO.setmode(GPIO.BOARD)   
    GPIO.setup(motoRPin1,GPIO.OUT)   # set pins to OUTPUT mode
    GPIO.setup(motoRPin2,GPIO.OUT)
    GPIO.setup(enablePin,GPIO.OUT)
        
    p = GPIO.PWM(enablePin,1000) # creat PWM and set Frequence to 1KHz
    p.start(0)

# mapNUM function: map the value from a range of mapping to another range.
def mapNUM(value,fromLow,fromHigh,toLow,toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow
	
# motor function: determine the direction and speed of the motor according to the input ADC value input
def motor(ADC):
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
    p.start(mapNUM(abs(value),0,128,0,100))
#    print ('The PWM duty cycle is %d%%\n'%(abs(value)*100/127))   # print PMW duty cycle.


def destroyMotor():
    p.stop()  # stop PWM


def startVideo(appState):

    now = datetime.datetime.now()
    appState.currentVideoName = f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}'
    print(f'video name is {appState.currentVideoName}')
    appState.videoProcess = subprocess.Popen(['raspivid', '-o', f'{appState.currentVideoName}.h264', '-t', '30000'])

def stopVideo(appState):
    if(appState.videoProcess != None):
        h264Name = f'{appState.currentVideoName}.h264'
        appState.videoProcess.terminate()
        appState.videoProcess = None
        boxProc = subprocess.Popen(['MP4Box', '-add', h264Name, f'{appState.currentVideoName}.mp4'])
        boxProc.wait()
        if os.path.exists(h264Name):
            os.remove(h264Name)
        appState.currentVideoName = ''




trigPin = 16
echoPin = 18
MAX_DISTANCE = 220          # define the maximum measuring distance, unit: cm
timeOut = MAX_DISTANCE*60   # calculate timeout according to the maximum measuring distance

def pulseIn(pin,level,timeOut): # obtain pulse time of a pin under timeOut
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
    
def getSonar():     # get the measurement results of ultrasonic module,with unit: cm
    GPIO.output(trigPin,GPIO.HIGH)      # make trigPin output 10us HIGH level 
    time.sleep(0.00001)     # 10us
    GPIO.output(trigPin,GPIO.LOW) # make trigPin output LOW level 
    pingTime = pulseIn(echoPin,GPIO.HIGH,timeOut)   # read plus time of echoPin
    distance = pingTime * 340.0 / 2.0 / 10000.0     # calculate distance with sound speed 340m/s 
    return distance
    
def setup(appState):
    GPIO.setmode(GPIO.BOARD)      # use PHYSICAL GPIO Numbering
    GPIO.setup(trigPin, GPIO.OUT)   # set trigPin to OUTPUT mode
    GPIO.setup(echoPin, GPIO.IN)    # set echoPin to INPUT mode
    appState.state = State.CLEARING


def startPlaying(appState):
    appState.state = State.PLAYING
    motor(128 + 128 * MOTOR_SPEED)
    appState.process = subprocess.Popen(['cvlc', 'disco.m4a', 'vlc://quit'])
    time.sleep(4)
    startVideo(appState)

def stopPlaying(appState):    
    appState.state = State.CLEARING
    appState.process = None
    motor(128)
    stopVideo(appState)

def findSomeone(appState):
    distance = getSonar() # get distance
    print(f'LOOKING: sonar returned distance of {distance}')
    if (distance > 5 and distance < DISTANCE_IN_CM):
        startPlaying(appState);


def startLooking(appState):
    appState.state = State.LOOKING

def waitForClear(appState):
    distance = getSonar() # get distance
    print(f'CLEARING: sonar returned distance of {distance}')
    if (distance >= DISTANCE_IN_CM):
        startLooking(appState);

def checkForEndOfSong(appState):
    if(appState.process == None):
        stopPlaying(appState);
    else:
        result = appState.process.poll();
        if (result != None):
            stopPlaying(appState);

def loop(appState):
    while(True):
        if(appState.state == State.LOOKING):
            findSomeone(appState);
        elif appState.state == State.PLAYING:
            checkForEndOfSong(appState);
        elif appState.state == State.CLEARING:
            waitForClear(appState)

        time.sleep(.2)
        

def destroy():
    destroyMotor()
    GPIO.cleanup()

appState = AppState(state=State.LOOKING,process=None)

if __name__ == '__main__':     # Program entrance
    setup(appState)
    setupMotor()
    try:
        loop(appState)
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()


    
