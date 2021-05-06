'''
Created on Apr 29, 2021

@author: Jeffrey Blum
'''
import glob, sys
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QIODevice, QObject, QMutex

# _UPDATE_INTERVAL = 3

class MetroMini(QObject):
    '''
    Wrapper class for communicating with the peripheral microcontroller over serial
    '''
    readyToWrite = pyqtSignal(str)
    readComplete = pyqtSignal()
    outputData = pyqtSignal(float)
    
    def begin(self):
        path = glob.glob("/dev/tty.usbserial-*")
        if len(path) == 1:
            path = path[0]
        else:
            if len(path) == 0:
                raise(RuntimeError, "No USB serial device connected")
                sys.exit()
            else:
                raise(RuntimeError, "More than one USB serial device connected")
                sys.exit()
        self.serialPort = QSerialPort(path)
        self.serialPort.setBaudRate(9600)
        self.serialPort.open(QIODevice.ReadWrite)
        self.lock = QMutex()
        self.buffer = bytearray()
        self.reqMsg = "request;"
        self.readyToWrite.connect(self.writeData)
        self.serialPort.readyRead.connect(self.readData)
        self.readyToWrite.emit(self.reqMsg)
    
    def readData(self):
        if self.lock.tryLock(5):
            bytesIn = self.serialPort.readAll()
            for b in bytesIn:
                if b == 10: # This translates to the \n character which means the message is complete
                    msg = self.buffer.decode().strip()
                    print("Received message:", msg)
                    self.outputData.emit(float(msg))
                    print("Requesting data from Metro Mini")
                    self.readyToWrite(self.reqMsg)
                    break
                elif b != 13: # Ignore '\r' character too
                    self.buffer.append(b)
            self.lock.unlock()
        else:
            print("Failed to acquire lock...")   
    
    def writeData(self, msg):
        self.lock.lock()
        self.serialPort.write(msg.encode())
        self.serialPort.waitForBytesWritten()
        print("Message sent:", msg)
        self.lock.unlock()
        
        