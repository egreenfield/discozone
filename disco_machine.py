
from disco import State,Events
from tapedeck import TapedeckCommand, TapedeckEvent
from disco_ball import DiscoBallCommand
from video_recorder import VideoRecorderCommand
from sonar import SonarCommand, SonarEvent
from state_machine import StateMachine
from timer_device import TimerEvent, TimerCommand
from datetime import datetime
import os
import logging
log = logging.getLogger(__name__)
import random

class DiscoMachine(StateMachine):
    
    def __init__(self,config,deviceMgr,danceClient):
        
        self.setConfig(config)
        self.deviceMgr = deviceMgr
        self.danceClient = danceClient
        self.fileIndex = random.randrange(1000)
        self.audioRepeatCount = 0
        StateMachine.__init__(self,
            initialState = State.LOOKING,
            transitions = {
                State.LOOKING: {
                    SonarEvent.PERSON_APPROACHING: lambda f,t,e : State.PLAYING if self.checkWorkingHours() else None,
                    Events.RemoteStart: State.PLAYING
                },
                State.PLAYING: {
                    SonarEvent.PERSON_LEFT: lambda f,t,e : State.LOOKING if config.silentWhenAlone else None,
                    TapedeckEvent.SONG_STOPPED: State.CLEARING,
                    Events.RemoteStop: State.LOOKING,
                },
                State.CLEARING: {
                    TimerEvent.TIMER_COMPLETE: State.LOOKING
                }
            },
            actions = {
                '': {
                    State.PLAYING: lambda event,s,o : self.startDiscoSession(event),
                    State.CLEARING: lambda e,s,o : self.startClearing(),
                    State.LOOKING: lambda e,s,o : self.endDiscoSession(),
                    '': lambda e,s,o: {
                        log.info(f'switching from {o} to {s} with event {e}')
                    }
                }
            }
        )

    def setConfig(self,config):
        self.config = config

        self.startTime = self.endTime = None
        if(config.workingHours != None):
            try:
                self.startTime = datetime.strptime(config.workingHours['start'],"%H:%M")
                self.endTime = datetime.strptime(config.workingHours['end'],"%H:%M")
            except ValueError:
                pass

    def checkWorkingHours(self):
        if self.startTime == None or self.endTime == None:
            return True 
        start = datetime.now().replace(hour=self.startTime.hour,minute=self.startTime.minute)
        end = datetime.now().replace(hour=self.endTime.hour,minute=self.endTime.minute)
        now = datetime.now()
        return (now >= start and now <= end)

    def pickSong(self):
        audioFile = self.config.audioFile
        if(audioFile[-1] == "/"):
            files = os.listdir(audioFile)
            if(self.audioRepeatCount >= self.config.audioRepeatCount):
                self.fileIndex = (self.fileIndex+1) % len(files)
                self.audioRepeatCount = 0
            self.audioRepeatCount += 1
            result = audioFile + files[self.fileIndex];
        else:
            result = audioFile
        return result


    def startDiscoSession(self,event):
        log.info(f'STARTING disco state with event {event}')
        nextSong = self.pickSong()
        danceID = event['id']

        if(self.config.music):
            self.deviceMgr.sendCommand("audio",TapedeckCommand.PLAY,data = {"song":nextSong})

        self.deviceMgr.sendCommand("sonar",SonarCommand.LOG,event['deviceID'],data = {
            "id":danceID
        })

        try:
             if(self.danceClient):
                  self.danceClient.registerNewDance(danceID,{"song":nextSong,"time":str(datetime.utcnow())})
        except:
             pass

        if(self.config.ball):
            self.deviceMgr.sendCommand("ball",DiscoBallCommand.SPIN)
        if(self.config.video):
            self.deviceMgr.sendCommand("video",VideoRecorderCommand.START,data={
                "danceID":danceID
            })

    def startClearing(self):
        self.endDiscoSession()
        self.deviceMgr.sendCommand("clearTimer",TimerCommand.START)

    def endDiscoSession(self):    
        self.deviceMgr.sendCommand("ball",DiscoBallCommand.STOP)
        self.deviceMgr.sendCommand("audio",TapedeckCommand.STOP)
        self.deviceMgr.sendCommand("video",VideoRecorderCommand.STOP)

    
    

