
from collections import deque
from threading import Condition, RLock
import disco
from disco import State

import logging
log = logging.getLogger(__name__)

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

    def setState(self,newState):
        log.debug(f'switching from {self.state} to {newState}')
        try:
            self.actions[self.state]['']()
        except KeyError:
            pass

        try:
            self.actions[self.state][newState]()
        except KeyError:
            pass
        try:
            self.actions[''][newState]()
        except KeyError:
            pass
        self.state = newState


    def processEvent(self,event):        
        log.debug(f'handling event {event}')
        targetState = None
        print(f'state map is {self.transitions[self.state]}')
        try:
            targetState = self.transitions[self.state][event]
        except KeyError: 
            pass
        if(targetState == None):
            try:
                targetState = self.transitions[''][event]
            except KeyError: 
                pass
        if callable(targetState):
            targetState = targetState(self.state, targetState)
        if (targetState == None):
            return
        self.setState(targetState)

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
    


