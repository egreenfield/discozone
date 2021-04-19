from dataclasses import dataclass, field
import json
import os

@dataclass
class Config:
    ball:bool = True
    music:bool = True
    video:bool = True    
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
                if 'devices' in configData:
                    f.deviceConfig = configData['devices']
        return f

