#!/usr/bin/env python3

from dataclasses import dataclass
from threading import Thread
import disco
import RPi.GPIO as GPIO
import devices
import time

from config import Config

from disco_machine import DiscoMachine
from webservice import RestService
import logging
import os

################################################################################################
# 
# Model and State
#
@dataclass
class AppState:
    machine: DiscoMachine = None
    deviceMgr: devices.DeviceManager = None
    running:bool = True
    config:Config = None

################################################################################################
# 
# General
#


def handleEvent(appState,device,event,data):
    appState.machine.addEvent(event)

def setup(appState):
    appState.config = Config.load('config.json')

    appState.deviceMgr = devices.DeviceManager()
    appState.deviceMgr.setEventHandler(lambda device, event, data : handleEvent(appState,device,event,data))
    Config.loadDevicesFromConfigData(appState.config,appState.deviceMgr)
    appState.deviceMgr.initDevices()

    if(appState.config.leader == None):
        appState.machine = DiscoMachine(appState.config,appState.deviceMgr)    
        appState.machine.setup()


def runMachine(appState):
    while(appState.running):
        appState.machine.pump()
        time.sleep(.2)        


def destroy(appState):
    appState.deviceMgr.shutdownDevices()
    appState.machine.shutdown()    
    GPIO.cleanup()

appState = AppState()

if __name__ == '__main__':     # Program entrance

    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    setup(appState)
    try:

        if(appState.config.leader == None):
            machineThread = Thread(target=runMachine,args=(appState,))
            machineThread.start()

        service = RestService(appState.machine,appState.deviceMgr)
        service.start()
            
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        print("INTERRUPT")
        appState.running = False        
        destroy(appState)

