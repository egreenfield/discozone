#!/usr/bin/env python3

from dataclasses import dataclass
from threading import Thread
import disco
import RPi.GPIO as GPIO
import time
from disco_machine import DiscoMachine
from sonar import Sonar

################################################################################################
# 
# Model and State
#

DISTANCE_IN_CM = 60

@dataclass
class AppState:
    machine: DiscoMachine = None
    sonar: Sonar = None

def findSomeone(appState):
    distance = appState.sonar.get() # get distance
    if(appState.machine.state == disco.State.LOOKING):
        print(f'LOOKING: sonar returned distance of {distance}')
    if (distance > 5 and distance < DISTANCE_IN_CM):
        appState.machine.addEvent(disco.Events.PersonApproaching)


################################################################################################
# 
# General
#

def setup(appState):
    appState.machine = DiscoMachine(disco.Features(video=False, music=True))
    appState.machine.setup()
    appState.sonar = Sonar()
    appState.sonar.setup()

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

