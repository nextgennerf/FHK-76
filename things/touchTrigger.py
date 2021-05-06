'''
Created on Apr 24, 2021

@author: Jeffrey Blum
'''
from PyQt5.QtCore import pyqtSignal, QState, QStateMachine
import asyncio as aio
from things.button import Button
from asyncio.tasks import FIRST_COMPLETED

class TouchTrigger(Button):
    '''
    Button subclass for the trigger which has a capacitive sensor
    '''
    touched = pyqtSignal()
    letGo = pyqtSignal()

    def __init__(self, sim):
        super().__init__(sim)
        self.stateLoop = QStateMachine()
        self.offState = QState()
        self.revState = QState()
        self.onState = QState()
        
        self.offState.addTransition(self, self.touched, self.revState)
        self.revState.addTransition(self, self.letGo, self.offState)
        self.revState.addTransition(self, self.pressed, self.onState)
        self.onState.addTransition(self, self.released, self.revState)
        
        for s in [self.offState, self.revState, self.onState]:
            self.stateLoop.addState(s)
        self.stateLoop.setInitialState(self.offState)
         
    def connectSimulator(self, name, sim):
        super().connectSimulator(name, sim)
        if self.simulated:
            self.touchEvent = aio.Event()
            sim.addEvent(name + " touch", self.touchEvent)
            self.relaxEvent = aio.Event()
            sim.addEvent(name + " relax", self.relaxEvent)
    
    async def loop(self):
        while True:
            if self.state == 0:
                await self.touchEvent.wait()
                self.state = 1
                print("Trigger is touched")
                self.touchEvent.clear()
            elif self.state == 1:
                pullTask = aio.create_task(self.pressEvent.wait())
                releaseTask = aio.create_task(self.releaseEvent.wait())
                done = (await aio.wait({pullTask, releaseTask}, return_when = FIRST_COMPLETED))[0]
                if pullTask in done:
                    self.state = 2
                    print("Trigger is pulled")
                    self.pressEvent.clear()
                elif releaseTask in done:
                    self.state = 0
                    print("Trigger is released")
                    self.releaseEvent.clear()
            elif self.state == 2:
                await self.relaxEvent.wait()
                self.state = 1
                print("Trigger is relaxed")
                self.relaxEvent.clear()