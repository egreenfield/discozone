#!/usr/bin/env python3

from dataclasses import dataclass
from threading import Thread
import disco
import RPi.GPIO as GPIO
import devices
import time
from remote import Remote

from tapedeck import Tapedeck
from video_recorder import VideoRecorder
from disco_ball import DiscoBall
from sonar import Sonar
from devices import RemoteDevice
from timer_device import TimerDevice


from config import Config

from disco_machine import DiscoMachine
from webservice import RestService
import os

import logging
log = logging.getLogger(__name__)

################################################################################################
# 
# Model and State
#

deviceMap = {
    "audio": Tapedeck,
    "video": VideoRecorder,
    "ball": DiscoBall,
    "sonar": Sonar,
    "remote": RemoteDevice,
    "timer": TimerDevice
}


class App:
    machine: DiscoMachine = None
    deviceMgr: devices.DeviceManager = None
    remote: Remote = None
    running:bool = True
    config:Config = None

################################################################################################
# 
# General
#


    def handleEvent(self,device,event,data):
        if (self.config.leader == None):
            self.machine.addEvent(event)
        else:
            self.remote.request(f'http://{self.config.leader}:8000/event/{event}')

    def setup(self):

        Config.setDeviceTypes(deviceMap)
        self.config = Config.load('config.json')

        self.remote = Remote()
        self.deviceMgr = devices.DeviceManager(self.remote)
        self.deviceMgr.setEventHandler(lambda device, event, data : self.handleEvent(device,event,data))
        Config.loadDevicesFromConfigData(self.config,self.deviceMgr)
        self.deviceMgr.initDevices()

        if(self.config.leader == None):
            self.machine = DiscoMachine(self.config,self.deviceMgr)    
            self.machine.setup()


    def runMachine(self):
        while(self.running):
            self.machine.pump()
            time.sleep(.2)        

    def run(self):
        if(self.config.leader == None):
            machineThread = Thread(target=lambda : self.runMachine())
            machineThread.start()

        service = RestService(self.machine,self.deviceMgr)
        service.start()



    def destroy(self):
        self.running = False        
        self.deviceMgr.shutdownDevices()
        if (self.machine):
            self.machine.shutdown()    
        GPIO.cleanup()

app = App()

if __name__ == '__main__':     # Program entrance

    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"),
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S')
    # fh = logging.FileHandler('logs/discoOutput.txt')
    # fh.setLevel(logging.DEBUG)
    # log.addHandler(fh)
    # logging.basicConfig(filename="logs/discoOutput.txt",
    #                         filemode='a',
    #                         format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    #                         datefmt='%H:%M:%S',
    #                         level=logging.DEBUG)
    app.setup()
    try:
        log.debug(f'Starting discozone, current directory is {os.getcwd()}')
        app.run()

    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        print("INTERRUPT")
        app.destroy()

