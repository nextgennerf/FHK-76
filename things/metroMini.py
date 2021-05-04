'''
Created on Apr 29, 2021

@author: Jeffrey Blum
'''
import serial, serial_asyncio
import asyncio as aio
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
        self.write(f"set {lcd.getTarget()};")
    
    @pyqtSlot(float)
    def setTarget(self, val):
        self.write(f"set {val};")
        
    
    def getPath(self):
        return self.mm.name
    
    '''
    This method can only be called by synchronous methods
    '''
    def write(self, msg):
        self.mm.write(msg.encode())
    
    # async def dataReady(self):
    #     while self.mm.in_waiting == 0:
    #         await aio.sleep(1.0)
    #     print("Data available")
    #     return
    
    async def loop(self):
        loop = aio.get_running_loop()
        with cf.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, lambda: self.mm.write("request;".encode()))
            print(f"Sending message: request;")
            data = await loop.run_in_executor(pool, lambda: self.mm.readline().rstrip("\\r\\n"))
        print(data)
        await self.display.update(float(data))
        await aio.sleep(_UPDATE_INTERVAL)
        