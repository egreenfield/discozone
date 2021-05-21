
from disco import State,Events
from tapedeck import TapedeckCommand, TapedeckEvent
from disco_ball import DiscoBallCommand
from video_recorder import VideoRecorderCommand
from sonar import SonarEvent
from state_machine import StateMachine
from timer_device import TimerEvent, TimerCommand
import logging
log = logging.getLogger(__name__)

class DiscoMachine(StateMachine):
    
    def __init__(self,config,deviceMgr,transitions = {},actions = {}):
        
        self.config = config
        self.deviceMgr = deviceMgr

        StateMachine.__init__(self,
            initialState = State.LOOKING,
            transitions = {
                State.LOOKING: {
                    SonarEvent.PERSON_APPROACHING: State.PLAYING,
                    Events.RemoteStart: State.PLAYING
                },
                State.PLAYING: {
                    SonarEvent.PERSON_LEFT: lambda f,t : State.LOOKING if config.silentWhenAlone else None,
                    TapedeckEvent.SONG_STOPPED: State.CLEARING,
                    Events.RemoteStop: State.LOOKING,
                },
                State.CLEARING: {
                    TimerEvent.TIMER_COMPLETE: State.LOOKING
                }
            },
            actions = {
                '': {
                    State.PLAYING: lambda : self.startDiscoSession(),
                    State.CLEARING: lambda : self.startClearing(),
                    State.LOOKING: lambda : self.endDiscoSession(),
                }
            }
        )

    def startDiscoSession(self):
        if(self.config.ball):
            self.deviceMgr.sendCommand("ball",DiscoBallCommand.SPIN)
        if(self.config.music):
            self.deviceMgr.sendCommand("audio",TapedeckCommand.START)
        if(self.config.video):
            self.deviceMgr.sendCommand("video",VideoRecorderCommand.START)

    def startClearing(self):
        self.endDiscoSession()
        self.deviceMgr.sendCommand("clearTimer",TimerCommand.START)

    def endDiscoSession(self):    
        self.deviceMgr.sendCommand("ball",DiscoBallCommand.STOP)
        self.deviceMgr.sendCommand("audio",TapedeckCommand.STOP)
        self.deviceMgr.sendCommand("video",VideoRecorderCommand.STOP)

    
    

