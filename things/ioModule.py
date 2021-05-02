'''
Created on Apr 26, 2021

@author: Jeffrey Blum
'''

import asyncio

class IOModule:
    '''
    This is the highest level class inherited by all modules.
    '''

    def __init__(self, sim):
        '''
        Inputs get constructed with a reference to the blaster for triggering events. Outputs don't need that.
        '''
        self.simulated = sim
        self.name = None
    
    '''
    Input loop methods need a standardized name so they can be gathered easily
    '''
    async def loop(self):
        while True:
            await asyncio.sleep(10)    
    
    '''
    Inputs need to send an event to the terminal simulator
    '''
    def connectSimulator(self):
        pass
    
    '''
    Simulated IO need names but we don't want that clogging the constructor.
    '''
    def setName(self, name):
        if self.simulated:
            self.name = name