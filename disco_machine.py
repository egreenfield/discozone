
import subprocess
from threading import Thread
from collections import deque
import threading

import disco
from tapedeck import TapedeckCommand, TapedeckEvent
from disco_ball import DiscoBallCommand
from video_recorder import VideoRecorderCommand
from sonar import SonarEvent

import logging
log = logging.getLogger(__name__)

class DiscoMachine:
    state:disco.State = disco.State.LOOKING
    events = deque()
    newEvents = deque()
    eventCondition = threading.Condition(threading.RLock())
    mode:disco.Mode = disco.Mode.Leader

    
    def __init__(self,config,deviceMgr):
        self.config = config
        self.deviceMgr = deviceMgr 

    def setup(self):
        None


    def startVideo(self):
        if(self.config.video == False):
            return
        self.deviceMgr.sendCommand("video",VideoRecorderCommand.START)

    def stopVideo(self):
        if(self.config.video == False):
            return
        self.deviceMgr.sendCommand("video",VideoRecorderCommand.STOP)

    def startAudio(self):
        if(self.config.music == False):
            return
        self.deviceMgr.sendCommand("audio",TapedeckCommand.START)
    
    def stopAudio(self):
        if(self.config.music == False):
            return
        self.deviceMgr.sendCommand("audio",TapedeckCommand.STOP)

    def foundSomeone(self):
        if(self.state != disco.State.LOOKING):
            return
        log.debug("found someone")
        self.startDiscoSession()

    def personLeft(self):
        if(self.state != disco.State.PLAYING):
            return
        if(self.config.silentWhenAlone == False):
            return
        self.endDiscoSession()

    def remoteStart(self):
        if(self.state != disco.State.LOOKING):
            return
        self.startDiscoSession()


    def startDiscoSession(self):
        self.setState(disco.State.PLAYING)
        self.deviceMgr.sendCommand("ball",DiscoBallCommand.SPIN)
        self.startAudio()
        self.startVideo()

    def endDiscoSession(self):    
        if(self.state != disco.State.PLAYING):
            return
        self.deviceMgr.sendCommand("ball",DiscoBallCommand.STOP)
        self.stopAudio()
        self.stopVideo()
        self.setState(disco.State.LOOKING)

    def startLooking(self):
        self.setState(disco.State.LOOKING)


    def shutdown(self):
        None
    
    def setState(self,newState):
        log.debug(f'switching from {self.state} to {newState}')
        self.state = newState

    def processEvent(self,event):
        log.debug(f'handling event {event}')
        if (event == SonarEvent.PERSON_APPROACHING):
            self.foundSomeone()
        elif (event == SonarEvent.PERSON_LEFT):
            self.personLeft()
        elif (event == TapedeckEvent.SONG_STOPPED):
            self.endDiscoSession()
        elif (event == disco.Events.RemoteStart):
            self.foundSomeone()
        elif (event == disco.Events.RemoteStop):
            self.endDiscoSession()

    def pump(self):
        with self.eventCondition:
            newEvents = self.newEvents
            self.newEvents = self.events
            self.events = newEvents

        for event in newEvents:
            self.processEvent(event)
        newEvents.clear()


    def addEvent(self,event):
        with self.eventCondition:
            self.newEvents.append(event)
    

