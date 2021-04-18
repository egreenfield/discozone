#!/usr/bin/env python3

from dataclasses import dataclass
from threading import Thread
import disco
import RPi.GPIO as GPIO
import time
from disco_machine import DiscoMachine
from sonar import Sonar
from webservice import RestService
import logging
import os

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
    # if(appState.machine.state == disco.State.LOOKING):
    #     print(f'LOOKING: sonar returned distance of {distance}')
    if (distance > 5 and distance < DISTANCE_IN_CM):
        appState.machine.addEvent(disco.Events.PersonApproaching)


################################################################################################
# 
# General
#

running = True

def setup(appState):
    appState.machine = DiscoMachine(
        disco.Features(
            video=True, 
            music=False,
            videoStorage="disco@192.168.1.100:~/Pictures/disco"
        )
    )
    appState.machine.setup()
    appState.sonar = Sonar()
    appState.sonar.setup()


def runMachine(appState):
    while(running):
        appState.machine.pump()
        # findSomeone(appState);
        time.sleep(.2)        

def runSonar(appState):
    while(running):
        findSomeone(appState);
        time.sleep(.2)        

def destroy(appState):
    appState.machine.shutdown()
    GPIO.cleanup()

appState = AppState()

if __name__ == '__main__':     # Program entrance

    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    setup(appState)
    try:
        sonarThread = Thread(target=runSonar,args=(appState,))
        sonarThread.start()

        machineThread = Thread(target=runMachine,args=(appState,))
        machineThread.start()

        service = RestService(appState.machine)
        service.start()
            
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        print("INTERRUPT")
        running = False        
        destroy(appState)

