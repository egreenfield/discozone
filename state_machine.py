
from collections import deque
from threading import Condition, RLock
import disco
from disco import State

import logging
log = logging.getLogger(__name__)
# log.setLevel("DEBUG")


class StateMachine:

    
    def __init__(self,transitions = {},initialState = None,actions = None):
        self.state = initialState
        self.events = deque()
        self.newEvents = deque()
        self.eventCondition = Condition(RLock())
        self.transitions = transitions
        self.actions = actions


    def setup(self):
        None

    def shutdown(self):
        None

    def setState(self,newState,event):
        log.debug(f'switching from {self.state} to {newState}')
        try:
            self.actions[''][''](event,newState,self.state)
        except KeyError:
            pass
        try:
            self.actions[self.state][''](event,newState,self.state)
        except KeyError:
            pass

        try:
            self.actions[self.state][newState](event,newState,self.state)
        except KeyError:
            pass
        try:
            self.actions[''][newState](event,newState,self.state)
        except KeyError:
            pass
        self.state = newState


    def processEvent(self,event):        
        log.debug(f'handling event {event}')
        targetState = None
        eventName = event['name']
        try:
            targetState = self.transitions[self.state][eventName]
        except KeyError: 
            pass
        if(targetState == None):
            try:
                targetState = self.transitions[''][eventName]
            except KeyError: 
                pass
        if callable(targetState):
            targetState = targetState(self.state, targetState,event)
        if (targetState == None):
            return
        self.setState(targetState,event)

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
    


