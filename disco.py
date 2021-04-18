import json
import os
from enum import Enum
from dataclasses import dataclass

class State(Enum):
    LOOKING = 1
    CLEARING = 2
    PLAYING = 3

class Events(Enum):
    PersonApproaching = 1
    SongStopped = 2
    RemoteStart = 3 
    RemoteStop = 4

@dataclass
class Features:
    ball:bool = True
    music:bool = True
    video:bool = True    
    videoStorage:str = None


    @classmethod
    def load(cls,jsonPath):
        f = Features()
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
        return f

