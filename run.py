#!/usr/bin/env python3

from dataclasses import dataclass
from threading import Thread
import disco
import RPi.GPIO as GPIO
import devices
import time

from tapedeck import Tapedeck
from video_recorder import VideoRecorder
from disco_ball import DiscoBall
from config import Config

from disco_machine import DiscoMachine
from sonar import Sonar
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


################################################################################################
# 
# General
#

running = True

deviceMap = {
    "audio": Tapedeck,
    "video": VideoRecorder,
    "ball": DiscoBall,
    "sonar": Sonar,
}

def loadDevicesFromConfigData(config,deviceMgr):
    deviceConfig = config.deviceConfig
    for aDevice in deviceConfig:
        typeName = aDevice['type']
        device = deviceMap[typeName]()
        if('config' in aDevice):
            device.setConfig(aDevice['config'])
        deviceMgr.addDevice(typeName,device)

def setup(appState):
    config = Config.load('config.json')

    appState.deviceMgr = devices.DeviceManager()
    appState.machine = DiscoMachine(config,appState.deviceMgr)    
    appState.deviceMgr.setEventHandler(lambda device, event, data : appState.machine.addEvent(event))

    loadDevicesFromConfigData(config,appState.deviceMgr)

    appState.deviceMgr.initDevices()

    appState.machine.setup()


def runMachine(appState):
    while(running):
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

        machineThread = Thread(target=runMachine,args=(appState,))
        machineThread.start()

        service = RestService(appState.machine)
        service.start()
            
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        print("INTERRUPT")
        running = False        
        destroy(appState)

