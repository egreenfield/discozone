from enum import Enum

class Mode(Enum):
    Leader = 1
    Follower = 2

class State(Enum):
    LOOKING = 1
    CLEARING = 2
    PLAYING = 3

class Events(Enum):
    PersonApproaching = 1
    SongStopped = 2
    RemoteStart = 3 
    RemoteStop = 4

