from uuid import uuid4

class Device:
    id = None
    def __init__(self):
        self.id = str(uuid4())
        None

    def setMgr(self,mgr):
        self.mgr = mgr

    def setId(self,id):
        self.id = id

    def init(self):
        None

    def shutdown(self):
        None

    def onCommand(self,id,data = None):
        None
    def raiseEvent(self,id,data = None):
        self.mgr.raiseEvent(self,id,data)        
    
    def setConfig(self,config):
        None


class DeviceManager:
    deviceMap: dict
    eventHandler  = None

    def __init__(self):
        self.deviceMap = {}
    
    def addDevice(self,deviceClass,device):
        devices = None
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


