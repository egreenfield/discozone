
import subprocess
from threading import Thread
from collections import deque
import threading

from tapedeck import Tapedeck
import disco
from disco_ball import DiscoBall
from video_recorder import VideoRecorder


# config
DISTANCE_IN_CM = 60

class DiscoMachine:
    state:disco.State = disco.State.CLEARING
    events = deque()
    newEvents = deque()
    eventCondition = threading.Condition(threading.RLock())

    tapedeck:Tapedeck = None
    ball:DiscoBall = None
    recorder:VideoRecorder = None
    
    def __init__(self,features):
        self.features = features
        self.tapedeck = Tapedeck(self)
        self.ball = DiscoBall()
        self.recorder = VideoRecorder()

    def setup(self):
        self.ball.init()



    def startVideo(self):
        if(self.features.video == False):
            return
        self.recorder.start()

    def stopVideo(self):
        if(self.features.video == False):
            return
        self.recorder.stop()

    def startAudio(self):
        if(self.features.music == False):
            return
        self.tapedeck.start()
    
    def stopAudio(self):
        if(self.features.music == False):
            return
        self.tapedeck.stop()

    def foundSomeone(self):
        if(self.state != disco.State.LOOKING):
            return
        self.startDiscoSession()

    def startDiscoSession(self):
        self.setState(disco.State.PLAYING)
        self.ball.spin()
        self.startAudio()
        self.startVideo()

    def endDiscoSession(self):    
        if(self.state != disco.State.PLAYING):
            return
        self.setState(disco.State.CLEARING)
        self.ball.stop()
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
        print(f'switching from{self.state} to {newState}')
        self.state = newState

    def processEvent(self,event):
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
    

