import glob
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QIODevice, QObject, QMutex

# _UPDATE_INTERVAL = 3

class MetroMini(QObject):
    """CLASS: MetroMini
    
    This class wraps the serial port used to communicate with the peripheral MetroMini processor.
    
    SIGNALS                                 SLOTS
    ------------------------    -----------------
    displayRXMessage   (str)    (Simulator) begin
    displayTXMessage   (str)    (str)   writeData
    newDataAvailable (float)
    printStatus        (str)
    """
    # TODO: Gracefully handle serial connection errors
    
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
    
    printStatus = pyqtSignal(str)
    """SIGNAL: printStatus
            
    Displays a temporary message on the simulator's status bar
            
    Broadcasts:
        str - The temporary message to display
            
    Connects to:
        QMainWindow.QStatusBar.showMessage (MainWindow.simulator)
    """
    
    displayTXMessage = pyqtSignal(str)
    """SIGNAL: displayTXMessage
            
    Displays a message sent over serial in the simulator window
            
    Broadcasts:
        str - The message to display
            
    Connects to:
        QLabel.showMessage (MainWindow.simulator.serialSentMsg)
    """
    
    displayRXMessage = pyqtSignal(str)
    """SIGNAL: displayRXMessage
            
    Displays a message received from serial in the simulator window
            
    Broadcasts:
        str - The message to display
            
    Connects to:
        QLabel.showMessage (MainWindow.simulator.serialRcvdMsg)
    """
    
    def begin(self):
        """SLOT: begin
                
        Launches the serial read/write signal loop
                
        Expects:
            Simulator - The simulator window, or None if simulation is not being used
                
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
                self.printStatus.emit("ERROR: No USB serial device connected")
            else:
                self.printStatus.emit("ERROR: More than one USB serial device connected")
        self.serialPort = QSerialPort(path)
        self.serialPort.setBaudRate(9600)
        self.serialPort.open(QIODevice.ReadWrite)
        self.lock = QMutex()
        self.buffer = bytearray()
        self.reqMsg = "request;"
        self.readyToWrite.connect(self.writeData)
        self.serialPort.readyRead.connect(self.readData)
        print(self.serialPort.children())
        self.readyToWrite.emit("request;")
    
    def connectSimulator(self, sim):
        """METHOD: connectSimulator
                
        Creates a connection between this object and the simulator window, if the program is running in simulation    `
                
        Called by:
            MainWindow.__init__
                
        Arguments:
            FHKSimulator: The simulator window
                
        Returns:
            none
        """
        self.sim = sim
        self.printStatus.connect(lambda msg: self.sim.statusBar().showMessage(msg, 10000))
        self.displayTXMessage.connect(self.sim.serialSentMsg.setText)
        self.displayRXMessage.connect(self.sim.serialRcvdMsg.setText)
    
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
                    self.displayRXMessage.emit(msg)
                    self.newDataAvailable.emit(float(msg))
                    self.printStatus.emit("Requesting data from Metro Mini")
                    self.readyToWrite.emit(self.reqMsg)
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
            readytoWrite, FeedbackDisplay.messageReady (MainWindow.psiDisplay)
        """
        self.lock.lock()
        self.serialPort.write(msg.encode())
        self.serialPort.waitForBytesWritten()
        self.displayTXMessage.emit(msg)
        self.lock.unlock()
        
        