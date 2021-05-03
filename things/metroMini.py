'''
Created on Apr 29, 2021

@author: Jeffrey Blum
'''
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal

class MetroMini(QObject):
    '''
    Wrapper class for communicating with the peripheral microcontroller over Serial
    '''
    updatePSI = pyqtSignal(float)

    def __init__(self, sim, lcd):
        '''
        Constructor
        '''
        super().__init__()
        self.simulated = sim
        self.updatePSI.connect(lcd.display()['double'])
    
    async def loop(self):
        if self.simulated:
            await asyncio.sleep(10)
    
    async def setPSI(self, psi):
        if self.simulated:
            if psi < self.psiTarget:
                print("Simulating rocket launch in 10 seconds.")
                await asyncio.sleep(10)
                self.updatePSI.emit(0.0)
                print("Simulated launch complete.")
            while(self.lcd.value() < self.psiTarget):
                await asyncio.sleep(1)