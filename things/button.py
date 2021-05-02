'''
Created on Apr 24, 2021

@author: Jeffrey Blum
'''
import asyncio as aio
from things.ioModule import IOModule

class Button(IOModule):
    '''
    Base class for normally-open button inputs
    '''
    
    def __init__(self, sim, **kwargs):
        '''
        Constructor
        '''
        super().__init__(sim)
        if self.simulated:
            self.state = kwargs.pop("initial_state") if "initial_state" in kwargs else False
        self.calls = kwargs
    
    def connectSimulator(self, name, sim):
        if self.simulated:
            self.name = name
            self.pressEvent = aio.Event()
            sim.addEvent(name + " press", self.pressEvent)
            self.releaseEvent = aio.Event()
            sim.addEvent(name + " release", self.releaseEvent)
            
    async def loop(self):
        while True:
            if self.state:
                await self.releaseEvent.wait()
                self.state = False
                if self.simulated:
                    print(self.name + " released")
                if "release_call" in self.calls:
                    self.calls["release_call"]()
                self.releaseEvent.clear()
            else:
                await self.pressEvent.wait()
                self.state = True
                if self.simulated:
                    print(self.name + " pressed")
                if "press_call" in self.calls:
                    self.calls["press_call"]()
                self.pressEvent.clear()