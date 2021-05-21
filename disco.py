from enum import Enum

class State:
    LOOKING = "DiscoState:Looking"
    PLAYING = "DiscoState:Playing"
    CLEARING = "DiscoState:Clearing"

class Events:
    RemoteStart = "DiscoEvent:RemoteStart" 
    RemoteStop = "DiscoEvent:RemoteStop" 

