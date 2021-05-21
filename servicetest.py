#!/usr/bin/env python3

from dataclasses import dataclass
from threading import Thread
import disco
import devices
import time
from remote import Remote
from config import Config
from webservice import RestService
import os

import logging
log = logging.getLogger(__name__)

################################################################################################
# 
# Model and State
#
class App:
    machine = None
    deviceMgr: devices.DeviceManager = None
    remote: Remote = None
    running:bool = True
    config:Config = None

################################################################################################
# 
# General
#

    def setup(self):
        self.config = Config.load('config.json')

        self.remote = Remote()
        self.deviceMgr = devices.DeviceManager(self.remote)
        self.deviceMgr.setEventHandler(lambda device, event, data : self.handleEvent(device,event,data))
        Config.loadDevicesFromConfigData(self.config,self.deviceMgr)
        self.deviceMgr.initDevices()



    def run(self):
        service = RestService(self.machine,self.deviceMgr)
        service.start()

app = App()

if __name__ == '__main__':     # Program entrance

    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"),
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S')
    app.setup()
    try:
        log.debug(f'Starting discozone, current directory is {os.getcwd()}')
        app.run()

    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        print("INTERRUPT")
        app.destroy()

