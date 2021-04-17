#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
from threading import Thread
from disco_machine import DiscoMachine
import disco
from dataclasses import dataclass

################################################################################################
# 
# Model and State
#

@dataclass
class AppState:
    machine: DiscoMachine = None


################################################################################################
# 
# Sonar
#


# config

DISTANCE_IN_CM = 60
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
    


def setupSonar(appState):
    GPIO.setmode(GPIO.BOARD)      # use PHYSICAL GPIO Numbering
    GPIO.setup(trigPin, GPIO.OUT)   # set trigPin to OUTPUT mode
    GPIO.setup(echoPin, GPIO.IN)    # set echoPin to INPUT mode

def findSomeone(appState):
    distance = getSonar() # get distance
    if(appState.machine.state == disco.State.LOOKING):
        print(f'LOOKING: sonar returned distance of {distance}')
    if (distance > 5 and distance < DISTANCE_IN_CM):
        appState.machine.addEvent(disco.Events.PersonApproaching)


# def waitForClear(appState):
#     distance = getSonar() # get distance
#     print(f'CLEARING: sonar returned distance of {distance}')
#     if (distance >= DISTANCE_IN_CM):
#         appState.machine.startLooking();


################################################################################################
# 
# General
#

def setup(appState):
    appState.machine = DiscoMachine(disco.Features(video=False, music=True))
    setupSonar(appState)
    appState.machine.setup()

def loop(appState):
    while(True):
        appState.machine.pump()
        findSomeone(appState);
        time.sleep(.2)        

def destroy(appState):
    appState.machine.shutdown()
    GPIO.cleanup()

appState = AppState()

if __name__ == '__main__':     # Program entrance
    setup(appState)
    try:
        # thread = Thread(target=loop,args=(appState,))
        # thread.run()
        # thread.join()
        loop(appState)
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy(appState)

