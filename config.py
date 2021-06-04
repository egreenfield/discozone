from dataclasses import dataclass, field
import json
import os


@dataclass
class Config:
    ball:bool = True
    music:bool = True
    video:bool = True    
    silentWhenAlone:bool = False
    videoStorage:str = None
    eventMethod:str = "post"
    deviceConfig:dict = field(default_factory=dict)
    # followers:list = field(default_factory=list)
    leader:str = None
    deviceMap = None
    audioFile = None
    workingHours = None


    # def loadConfig(self,name,data,configName = None):
    #     srcName = configName or name
    #     if name in data:
    #         setattr(self,name,data[srcName])

    @classmethod
    def setDeviceTypes(cls,deviceMap):
        cls.deviceMap = deviceMap

    @classmethod
    def load(cls,jsonPath):
        f = Config()
        if os.path.exists(jsonPath):
            with open(jsonPath) as fh:
                configData = json.load(fh)
                if 'ball' in configData:
                    f.ball = configData['ball']
                if 'music' in configData:
                    f.music = configData['music']
                if 'video' in configData:
                    f.video = configData['video']
                if 'videoStorage' in configData:
                    f.videoStorage = configData['videoStorage']
                if 'silentWhenAlone' in configData:
                    f.silentWhenAlone = configData['silentWhenAlone']
                if 'devices' in configData:
                    f.deviceConfig = configData['devices']
                if 'leader' in configData:
                    f.leader = configData['leader']
                f.serverConfig = configData.get('serverConfig')
                f.audioFile = configData.get('audioFile')
                f.workingHours = configData.get('workingHours',None)
                f.storageOptions = configData.get('storage',{})
                f.audioRepeatCount = configData.get('audioRepeatCount',1)
        return f


    @classmethod
    def loadDevicesFromConfigData(cls,config,app):
        deviceConfig = config.deviceConfig
        deviceMgr = app.deviceMgr

        for aDevice in deviceConfig:
            if ('enabled' in aDevice and aDevice['enabled'] == False):
                continue
            typeName = aDevice['type']
            device = cls.deviceMap[typeName](app)
            if ('id' in aDevice):
                device.setId(aDevice['id'])
            if('class' in aDevice):
                device.setClass(aDevice['class'])
            if('config' in aDevice):
                device.setConfig(aDevice['config'],config)
            deviceMgr.addDevice(device)
