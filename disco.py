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
