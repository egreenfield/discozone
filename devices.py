from uuid import uuid4
from  concurrent.futures import ThreadPoolExecutor
import requests

class Device:
    id = None
    def __init__(self):
        self.id = str(uuid4())
        self.className = "generic"
        None

    def setMgr(self,mgr):
        self.mgr = mgr

    def setId(self,id):
        self.id = id

    def setClass(self,className):
        self.className = className

    def init(self):
        None

    def shutdown(self):
        None

    def onCommand(self,cmd,data = None):
        None
    def raiseEvent(self,event,data = None):
        self.mgr.raiseEvent(self,event,data)        
    
    def setConfig(self,config):
        None


class Remote(Device):

    def setConfig(self,config):
        self.location = config['location']

    def onCommand(self,cmd,data = None):
        self.mgr.request(f'http://{self.location}:8000/command/{self.className}/{self.id}/{cmd}')

class DeviceManager:
    deviceMap: dict
    eventHandler  = None

    def __init__(self):
        self.deviceMap = {}
        self.remotePool = ThreadPoolExecutor(max_workers=10)
    
    @staticmethod
    def handleRequest(url):
        print(f'fetching {url}')
        requests.get(url)

    def request(self,url):
        self.remotePool.submit(DeviceManager.handleRequest,url)
    
    
    def addDevice(self,device):
        devices = None
        deviceClass = device.className

        if (deviceClass in self.deviceMap):
            devices = self.deviceMap[deviceClass]
        else:
            devices = self.deviceMap[deviceClass] = []
        devices.append(device)
        device.setMgr(self)
    
    def getFirstDevice(self,deviceClass):
        if (deviceClass in self.deviceMap):
            devices = self.deviceMap[deviceClass]
            if len(devices):
                return devices[0]
        return None

    def getDevices(self,deviceClass):
        if (deviceClass in self.deviceMap):
            return self.deviceMap[deviceClass]
        return []

    def execRemoteCommand(self, deviceClass, cmd, deviceId, data = None):
        self.sendCommand(deviceClass,cmd,deviceId,data)

    def sendCommand(self,deviceClass,cmd,deviceId = None, data = None):
        #print(f'sending command {deviceClass} {deviceId} {cmd}')
        devices = self.getDevices(deviceClass)
        for aDevice in devices:
            #print(f'examining {deviceClass} {aDevice.id}')
            if(deviceId == None or deviceId == aDevice.id):
                aDevice.onCommand(cmd,data)

    def setEventHandler(self,eventHandler):
        self.eventHandler = eventHandler

    def raiseEvent(self,device,id,data = None):
        self.eventHandler and self.eventHandler(device,id,data)

    def initDevices(self):
        for aName in self.deviceMap:
            devices = self.deviceMap[aName]
            for aDevice in devices:
                aDevice.init()

    def shutdownDevices(self):
        for aName in self.deviceMap:
            devices = self.deviceMap[aName]
            for aDevice in devices:
                aDevice.shutdown()


