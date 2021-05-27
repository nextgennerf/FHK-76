import glob
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QIODevice, QObject, QMutex, QMutexLocker

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
    
    newDataAvailable = pyqtSignal(float)
    """SIGNAL: newDataAvailable
            
    Emitted when a new pressure value has been received from the MetroMini
            
    Broadcasts:
        float - The new value
            
    Connects to:
        DisplayState.updateDisplay (MainWindow.psiDisplay.defaultState)
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
        """
        path = glob.glob("/dev/tty.usbserial-*")
        path = path[0]
        self.serialPort = QSerialPort(path)
        self.serialPort.setBaudRate(9600)
        self.lock = QMutex()
        self.buffer = bytearray()
        self.serialPort.readyRead.connect(self.readData)
        self.serialPort.open(QIODevice.ReadWrite)
    
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
        self.printStatus.connect(lambda msg: self.sim.statusBar().showMessage(msg, 3000))
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
        with QMutexLocker(self.lock):
            self.printStatus.emit("Lock acquired for reading")
            bytesIn = self.serialPort.readAll()
            for b in bytesIn:
                if b == b'\n': # This translates to the \n character which means the message is complete
                    msg = self.buffer.decode().strip()
                    self.displayRXMessage.emit(msg)
                    if msg != "ready":
                        self.newDataAvailable.emit(float(msg))
                    self.buffer = bytearray() # Clear buffer
                elif b != b'\r': # Ignore '\r' character too
                    self.buffer = self.buffer + b
    
    def writeData(self, msg):
        """SLOT: writeData
                
        Writes data to the serial port
                
        Expects:
            str - The message to be sent
                
        Connects to:
            FeedbackDisplay.messageReady (MainWindow.psiDisplay)
        """
        with QMutexLocker(self.lock):
            self.printStatus.emit("Lock acquired for writing")
            self.serialPort.write(msg.encode())
            self.serialPort.waitForBytesWritten()
            self.printStatus.emit("Serial write complete")
            self.displayTXMessage.emit(msg)
        
        