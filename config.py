from dataclasses import dataclass, field
import json
import os

from tapedeck import Tapedeck
from video_recorder import VideoRecorder
from disco_ball import DiscoBall
from sonar import Sonar
from devices import Remote

deviceMap = {
    "audio": Tapedeck,
    "video": VideoRecorder,
    "ball": DiscoBall,
    "sonar": Sonar,
    "remote": Remote
}

@dataclass
class Config:
    ball:bool = True
    music:bool = True
    video:bool = True    
    silentWhenAlone:bool = False
    videoStorage:str = None
    deviceConfig:dict = field(default_factory=dict)
    # followers:list = field(default_factory=list)
    # leader:str = None


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
        return f


    @staticmethod
    def loadDevicesFromConfigData(config,deviceMgr):
        deviceConfig = config.deviceConfig
        for aDevice in deviceConfig:
            typeName = aDevice['type']
            device = deviceMap[typeName]()
            if ('id' in aDevice):
                device.setId(aDevice['id'])
            if('class' in aDevice):
                device.setClass(aDevice['class'])
            if('config' in aDevice):
                device.setConfig(aDevice['config'])
            deviceMgr.addDevice(device)
