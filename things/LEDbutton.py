'''
Created on Apr 24, 2021

@author: Jeffrey Blum
'''
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal
from things.button import Button

class LEDButton(Button, QObject):
    '''
    Button subclass with LED ring
    '''
    updateGUI = pyqtSignal()

    def __init__(self, sim, buttons, modeID):
        '''
        Constructor
        '''
        Button.__init__(self, sim)
        QObject.__init__(self)
        self.modeID = modeID
        self.updateGUI.connect(buttons.button(modeID).click)
        

    def connectSimulator(self, name, sim):
        if self.simulated:
            self.pressEvent = asyncio.Event()
            sim.addEvent(name + " press", self.pressEvent)
            
    async def loop(self):
        while True:
            await self.pressEvent.wait()
            if not self.state:
                print(self.name + " pressed")
                self.state = True
                self.updateGUI.emit()
                self.pressEvent.clear()
    
    def turnOn(self):
        if self.name is not None:
            print(self.name + " LED is now on")
    
    def turnOff(self):
        if self.name is not None:
            print(self.name + " LED is now off")