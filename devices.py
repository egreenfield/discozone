from uuid import uuid4
import logging
log = logging.getLogger(__name__)


class Device:
    id = None
    def __init__(self,app):
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

    def onCommand(self,cmd,data = {}):
        None
    def raiseEvent(self,eventName,data = None):
        event = {
            "name": eventName,
            "id": str(uuid4()),
            "data": data,
            "deviceID": self.id,
            "deviceClass": self.className,
        }
        self.mgr.raiseEvent(event)
        return event

    def setConfig(self,config,globalConfig):
        None


class RemoteDevice(Device):

    def setConfig(self,config,globalConfig):
        self.location = config['location']

    def onCommand(self,cmd,data = {}):
        self.mgr.remote.postUrl(f'http://{self.location}:8000/command',{
            "className":self.className,
            "id":self.id,
            "command":cmd,
            "data":data
        })


class DeviceManager:
    deviceMap: dict
    eventHandler  = None

    def __init__(self,remote):
        self.deviceMap = {}
        self.remote = remote


    def request(self,url):
        self.remote.getUrl(url)


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

    def execRemoteCommand(self, deviceClass, cmd, deviceId, data = {}):
        self.sendCommand(deviceClass,cmd,deviceId,data)

    def sendCommand(self,deviceClass,cmd,deviceId = None, data = {}):

        devices = self.getDevices(deviceClass)
        for aDevice in devices:
            #print(f'examining {deviceClass} {aDevice.id}')
            if(deviceId == None or deviceId == aDevice.id):
                log.debug(f'sending command {deviceClass} {aDevice.id} {cmd}')
                aDevice.onCommand(cmd,data)

    def setEventHandler(self,eventHandler):
        self.eventHandler = eventHandler

    def raiseEvent(self,event):
        self.eventHandler and self.eventHandler(event)

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
