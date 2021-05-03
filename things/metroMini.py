'''
Created on Apr 29, 2021

@author: Jeffrey Blum
'''
import asyncio, serial
import concurrent.futures as cf
from PyQt5.QtCore import QObject, pyqtSlot

_UPDATE_INTERVAL = 1.0

class MetroMini(QObject):
    '''
    Wrapper class for communicating with the peripheral microcontroller over Serial
    '''

    def __init__(self, port, lcd):
        '''
        Constructor
        '''
        super().__init__()
        self.mm = serial.Serial(port, 9600)  
        self.display = lcd
        lcd.setTarget.connect(lambda new: self.setTarget(new))
        self.mm.write(f"set {lcd.getTarget()}.")
    
    @pyqtSlot(int)
    def setTarget(self, val):
        self.mm.write(f"set {val}.")
    
    def getPath(self):
        return self.mm.name
    
    async def getReturn(self):
        loop = asyncio.get_running_loop()
        with cf.ThreadPoolExecutor() as pool:
            data = await loop.run_in_executor(pool, self.mm.readline)
        return data.rstrip("\r\n")
    
    async def loop(self):
        self.mm.write("request.")
        newValue = await self.getReturn()
        await self.display.update(float(newValue))
        await asyncio.sleep(_UPDATE_INTERVAL)
        