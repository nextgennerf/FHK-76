import glob
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QIODevice, QObject, QMutex, QMutexLocker

# _UPDATE_INTERVAL = 3

class MetroMini(QObject):
    """CLASS: MetroMini
    
    This class wraps the serial port used to communicate with the peripheral Metro Mini processor.
    
    SIGNALS                                 SLOTS
    ------------------------    -----------------
    broadcast          (str)    (Simulator) begin
    displayRXMessage   (str)    ()       readData
    displayTXMessage   (str)    (str)   writeData
    newDataAvailable (float)
    printStatus        (str)
    ready                 ()
    """
    # TODO: Gracefully handle serial connection errors
    
    newDataAvailable = pyqtSignal(float)
    """SIGNAL: newDataAvailable
            
    Emitted when a new pressure value has been received from the Metro Mini
            
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
    
    broadcast = pyqtSignal(str)
    """SIGNAL: broadcast
            
    This signal is called when a message needs to be written to serial. It exists to ensure that the write signal is emitted in the correct thread.
            
    Broadcasts:
        str - The message to be sent
            
    Connects to:
        QState.exited (MainWindow.psiDisplay.waitState), (MainWindow.psiDisplay.requestTimer) QTimer.timeout, writeData
    """
    
    ready = pyqtSignal()
    """SIGNAL: ready
            
    Announces that the Metro Mini is ready for data exchange
            
    Broadcasts:
        none
            
    Connects to:
        MainWindow.initializeSerialObjects
    """
    
    close = pyqtSignal()
    
    def begin(self):
        """SLOT: begin
                
        Launches the serial read/write signal loop
                
        Expects:
            none
                
        Connects to:
            QThread.started
        """
        path = glob.glob("/dev/tty.usbserial-*")
        self.serialPort = None
        try:
            path = path[0]
        except IndexError:
            self.displayRXMessage.emit("No serial connected")
            self.ready.emit()
        else:
            self.serialPort = QSerialPort(path)
            self.serialPort.setBaudRate(9600)
            self.buffer = bytearray()
            self.serialPort.readyRead.connect(self.readData)
            self.close.connect(self.serialPort.close)
            self.serialPort.open(QIODevice.ReadWrite)
        finally:
            self.lock = QMutex()
            self.broadcast.connect(self.writeData)
    
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
        self.printStatus.connect(lambda msg: self.sim.statusBar().showMessage(msg, 5000))
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
            bytesIn = self.serialPort.readAll()
            for b in bytesIn:
                if b == b'\n': # This translates to the \n character which means the message is complete
                    msg = self.buffer.decode().strip()
                    self.displayRXMessage.emit(msg)
                    if msg == "ready":
                        self.ready.emit()
                    else:
                        self.newDataAvailable.emit(float(msg))
                    self.printStatus.emit("Serial read complete")
                    self.buffer = bytearray() # Clear buffer
                elif b != b'\r': # Ignore '\r' character too
                    self.buffer = self.buffer + b
    
    def writeData(self, msg):
        """SLOT: writeData
                
        Writes data to the serial port
                
        Expects:
            str - The message to be sent
                
        Connects to:
            broadcast
        """
        with QMutexLocker(self.lock):
            if self.serialPort is not None:
                self.serialPort.write(msg.encode())
                self.serialPort.waitForBytesWritten()
                self.printStatus.emit("Serial write complete")
            if msg != "request;": # This message prevents all others from being visible, and we know it's being sent if values are coming back
                self.displayTXMessage.emit(msg)