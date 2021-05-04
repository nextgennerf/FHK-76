'''
Created on Apr 29, 2021

@author: Jeffrey Blum
'''
import serial_asyncio, random
import asyncio as aio
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.Qt import pyqtSignal

#_UPDATE_INTERVAL = 5.0

class MetroMini(QObject):
    '''
    Wrapper class for communicating with the peripheral microcontroller over serial using a custom asynchronous protocol
    '''

    def __init__(self, path, lcd):
        '''
        Constructor
        '''
        super().__init__()
        
        self.path = path
        
        self.display = lcd
        lcd.setTarget.connect(self.setTarget)
        
        eLoop = aio.get_running_loop()
        coro = serial_asyncio.create_serial_connection(eLoop, self.SerialIO, path, baudrate = 9600)
        _, self.protocol = eLoop.run_until_complete(coro)
        

    @pyqtSlot(float)
    def setTarget(self, val):
        self.writeBuffer.append(f"set {float(val)};")
    
    @pyqtSlot(float)
    def setValue(self, val):
        self.display.update(val)
    
    def getPath(self):
        return self.path
    
    async def loop(self):
        while True:
            self.protocol.write("request;")
            await aio.sleep(5)
            print("Restarting loop...")
    
    '''
    This inner class represents the communication protocol
    '''
    class SerialIO(aio.Protocol, QObject):
        outputData = pyqtSignal(float)
        readBuffer = bytearray()
        eom = False
        
        def connect_signal(self, caller):
            self.outputData.connect(caller.setValue)
        
        def connection_made(self, transport):
            self.transport = transport
        
        def data_received(self, data):
            for b in data:
                if b == 13: # This translates to the \r character which means the message is complete
                    self.eom = True
                    break
                self.readBuffer.append(b)
            if self.eom:
                msg = self.readBuffer.decode().strip()
                print("Received message:", msg)
                self.outputData.emit(float(msg))
                self.eom = False
        
        def write(self, msg):
            print(f"Writing message: {msg}...")
            self.transport.write(msg.encode())
            print("...done")
        
        