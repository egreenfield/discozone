from enum import Enum

class Mode(Enum):
    Leader = 1
    Follower = 2

class State(Enum):
    LOOKING = 1
    PLAYING = 3

class Events:
    RemoteStart = "DiscoEvent:RemoteStart" 
    RemoteStop = "DiscoEvent:RemoteStop" 

