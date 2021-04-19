
import subprocess
from threading import Thread
from collections import deque
import threading

import disco
from tapedeck import TapedeckCommand
from disco_ball import DiscoBall, DiscoBallCommand
from video_recorder import VideoRecorder, VideoRecorderCommand

import logging
log = logging.getLogger(__name__)

# config
DISTANCE_IN_CM = 60

class DiscoMachine:
    state:disco.State = disco.State.CLEARING
    events = deque()
    newEvents = deque()
    eventCondition = threading.Condition(threading.RLock())
    mode:disco.Mode = disco.Mode.Leader

    ball:DiscoBall = None
    recorder:VideoRecorder = None
    
    def __init__(self,features,deviceMgr):
        self.features = features
        self.ball = DiscoBall()
        self.recorder = VideoRecorder(features.videoStorage)
        self.deviceMgr = deviceMgr 

    def setup(self):
        self.ball.init()



    def startVideo(self):
        if(self.features.video == False):
            return
        self.deviceMgr.sendCommand("video",VideoRecorderCommand.START)
        self.recorder.onCommand(VideoRecorderCommand.START)

    def stopVideo(self):
        if(self.features.video == False):
            return
        self.deviceMgr.sendCommand("video",VideoRecorderCommand.STOP)
        self.recorder.onCommand(VideoRecorderCommand.STOP)

    def startAudio(self):
        if(self.features.music == False):
            return
        self.deviceMgr.sendCommand("audio",TapedeckCommand.START)
    
    def stopAudio(self):
        if(self.features.music == False):
            return
        self.deviceMgr.sendCommand("audio",TapedeckCommand.STOP)

    def foundSomeone(self):
        if(self.state != disco.State.LOOKING):
            return
        self.startDiscoSession()

    def remoteStart(self):
        if(self.state != disco.State.LOOKING):
            return
        self.startDiscoSession()


    def startDiscoSession(self):
        self.setState(disco.State.PLAYING)
        self.deviceMgr.sendCommand("ball",DiscoBallCommand.SPIN)
        self.ball.onCommand(DiscoBallCommand.SPIN)
        self.startAudio()
        self.startVideo()

    def endDiscoSession(self):    
        if(self.state != disco.State.PLAYING):
            return
        self.setState(disco.State.CLEARING)
        self.deviceMgr.sendCommand("ball",DiscoBallCommand.STOP)
        self.ball.onCommand(DiscoBallCommand.STOP)
        self.stopAudio()
        self.stopVideo()

    def startLooking(self):
        self.setState(disco.State.LOOKING)

    def waitForClear(self):
        if(self.state != disco.State.CLEARING):
            return
        self.startLooking()

    def shutdown(self):
        self.ball.shutdown()
    
    def setState(self,newState):
        log.debug(f'switching from {self.state} to {newState}')
        self.state = newState

    def processEvent(self,event):
        log.debug(f'handling event {event}')
        if (event == disco.Events.PersonApproaching):
            self.foundSomeone()
        elif (event == disco.Events.SongStopped):
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

        self.waitForClear()

    def addEvent(self,event):
        with self.eventCondition:
            self.newEvents.append(event)
    

