import glob, sys
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QIODevice, QObject, QMutex

# _UPDATE_INTERVAL = 3

class MetroMini(QObject):
    """CLASS: MetroMini
    
    This class wraps the serial port used to communicate with the peripheral MetroMini processor.
    
    SIGNALS                               SLOTS
    ------------------------    ---------------
    newDataAvailable (float)    ()        begin
                                (str) writeData
    """
    
    readyToWrite = pyqtSignal(str)
    """SIGNAL: readyToWrite
            
    Emitted internally when a message can be sent as soon as the serial port is available
            
    Broadcasts:
        str - The message to be sent
            
    Connects to:
        MetroMini.writeData
    """
    
    newDataAvailable = pyqtSignal(float)
    """SIGNAL: newDataAvailable
            
    Emitted when a new pressure value has been received from the MetroMini
            
    Broadcasts:
        float - The new value
            
    Connects to:
        FeedbackDisplay.DisplayState.updateDisplay (MainWindow.psiDisplay.defaultState)
    """
    
    def begin(self):
        """SLOT: begin
                
        Launches the serial read/write signal loop
                
        Expects:
            none
                
        Connects to:
            QThread.started
        
        Emits:
            readyToWrite
        """
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
        """SLOT: readData
                
        Reads data from the serial port when it's available
                
        Expects:
            none
                
        Connects to:
            QSerialPort.readyRead
        
        Emits:
           newDataAvailable
        """
        if self.lock.tryLock(5):
            bytesIn = self.serialPort.readAll()
            for b in bytesIn:
                if b == 10: # This translates to the \n character which means the message is complete
                    msg = self.buffer.decode().strip()
                    #TODO: print("Received message:", msg)
                    self.newDataAvailable.emit(float(msg))
                    #TODO: print("Requesting data from Metro Mini")
                    self.readyToWrite(self.reqMsg)
                    break
                elif b != 13: # Ignore '\r' character too
                    self.buffer.append(b)
            self.lock.unlock()
        # else:
        #     #TODO: print("Failed to acquire lock...")   
    
    def writeData(self, msg):
        """SLOT: writeData
                
        Writes data to the serial port
                
        Expects:
            str - The message to be sent
                
        Connects to:
            FeedbackDisplay.messageReady (MainWindow.psiDisplay)
        """
        self.lock.lock()
        self.serialPort.write(msg.encode())
        self.serialPort.waitForBytesWritten()
        #TODO: print("Message sent:", msg)
        self.lock.unlock()
        
        