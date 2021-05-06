import threading
from PyQt5.QtCore import QObject, pyqtSignal, QMutex

_DELAY = 1.0 # Represents the time delay between the last GUI button press and the display returning to normal

#TODO: add determination of how data should be output

class FeedbackDisplay(QObject):
    """CLASS: FeedbackDisplay
    
    This class wraps a QLCDNumber in the GUI so it can keep track of a target value.
    
    SIGNALS                                 SLOTS
    ---------------------    --------------------
    displayNumer  (float)    (float) changeTarget
    sendMessage     (str)    (float)       output
    """
    
    sendMessage = pyqtSignal(str)
    """SIGNAL: sendMessage
    
    Emitted when the user uses the GUI to change the target value so the peripheral controller can be notified
    
    Broadcasts:
        str - A message to be delivered to the peripheral controller
    
    Connects to:
        MetroMini.writeData
    """
    
    displayNumber = pyqtSignal(float)
    """SIGNAL: displayNumber
    
    Alerts the wrapped QLCDNumber needs to change the number it's displaying
    
    Broadcasts:
        float - The number to be displayed
    
    Connects to:
        QLCDNumber.display
    """

    def __init__(self, lcd, targetVal):
        super().__init__()
        self.lcd = lcd
        self.target = float(targetVal)
        self.value = 0.0
        self.changing = False
        self.timer = None
        self.lock = QMutex()
        self.displayNumber.connect(lcd.display)
        self.displayNumber.emit(self.value)
        self.sendMessage.emit(f"set {self.target};")
    
    def changeTarget(self, delta):
        """SLOT: changeTarget
        
        Applies a numeric change to the stored target value and directs the QLCDNumber to show that change.
        
        Expect:
            float: The amount by which to shift the target value
        
        Connects to:
            QPushButton.clicked (MainWindow.fpsUpButton, MainWindow.fpsDownButton, MainWindow.psiUpButton, MainWindow.psiDownButton)
        """
        if self.lock.tryLock():  # This method can be called many times in rapid succession so it's ok if it can't
            self.changing = True # acquire the lock as long as it was acquired by a previous call to this method
        if self.changing:
            self.target += float(delta)
            if delta > 0:
                self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                                       "border-radius: 8px;\n"
                                       "color: #00FF00")
            elif delta < 0:
                self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                                       "border-radius: 8px;\n"
                                       "color: #FF0000")
            self.displayNumber.emit(self.target)
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(_DELAY, self.finalize)
            self.timer.start()
        
    def finalize(self):
        """METHOD: finalize
        
        Alert the rest of the system that the target value has changed and instructs the QLCDNumber to resume displaying current values
        
        Called by:
            changeTarget
        
        Arguments:
            none
        
        Returns:
            none
        
        Emits:
            displayNumber, sendMessage
        """
        self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                               "border-radius: 8px;\n"
                               "color: #000000")
        self.displayNumber.emit(self.value)
        self.sendMessage.emit(f"set {self.target};")
        self.changing = False
        self.lock.unlock()
    
    def output(self, value):
        """SLOT: output
        
        Instructs the QLCDNumber to update the displayed value only if the display isn't doing something else already
        
        Expects:
            float - The new number to display
        
        Connects to:
            MetroMini.outputData
        
        Emits:
            displayValue
        """
        self.lock.lock()
        self.value = value
        self.displayNumber.emit(value)
        self.lock.unlock()
    
    def getTarget(self):
        """METHOD: getTarget
        
        Returns the current target value
        
        Called by:
            TODO: FeedbackDisplay.getTarget callers
        
        Arguments:
            none
        
        Returns:
            float - The current target value
        """
        return self.target