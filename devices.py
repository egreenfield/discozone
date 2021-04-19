class Device:
    def __init__(self):
        None

    def setMgr(self,mgr):
        self.mgr = mgr

    def init(self):
        None

    def shutdown(self):
        None

    def onCommand(id,data = None):
        None
    def raiseEvent(id,data):
        self.mgr.raiseEvent()        

class DeviceManager:
    deviceMap: dict

    def __init__(self):
        self.deviceMap = {}
    
    def addDevice(self,name,device):
        devices = None
        if (name in self.deviceMap):
            devices = self.deviceMap[name]
        else:
            devices = self.deviceMap[name] = []
        devices.append(device)
        device.setMgr(self)
    
    def getFirstDevice(self,name):
        if (name in self.deviceMap):
            namedDevices = self.deviceMap[name]
            if len(namedDevices):
                return namedDevices[0]
        return None

    def getDevices(self,name):
        if (name in self.deviceMap):
            return self.deviceMap[name]
        return []

    def sendCommand(self,name,cmd,data = None):
        devices = self.getDevices(name)
        for aDevice in devices:
            aDevice.onCommand(cmd,data)

    def shutdown(self):
        for aName in self.deviceMap:
            devices = self.deviceMap[aName]
            for aDevice in devices:
                aDevice.shutdown()

