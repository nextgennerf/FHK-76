import threading
from PyQt5.QtCore import QObject, pyqtSignal, QMutex

_DELAY = 1.0 # Represents the time delay between the last GUI button press and the display returning to normal

class FeedbackDisplay(QObject):
    """CLASS: FeedbackDisplay
    
    This class wraps a QLCDNumber in the GUI so it can keep track of a target value.
    
    SIGNALS                  SLOTS
    ---------------------    -----
    setTarget     (float)     none
    displayNumber (float)
    """
    
    setTarget = pyqtSignal(float)
    """SIGNAL: setTarget
    
    Emitted when the user uses the GUI to change the target value
    
    Broadcasts:
        float - The new target value
    
    Connects to:
        none
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
        self.setTarget.emit(self.target)
    
    def changeTarget(self, delta):
        """METHOD: changeTarget
        
        Applies a numeric change to the stored target value and directs the GUI to show that change.
        
        Called by:
            none
        
        Arguments:
            int/float: The amount by which to shift the target value
        
        Returns:
            none
        
        Emits:
            displayNumber
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
        
        Alert the rest of the system that the target value has changed and instructs the GUI to resume displaying current values
        
        Called by:
            changeTarget
        
        Arguments:
            none
        
        Returns:
            none
        
        Emits:
            displayNumber, setTarget
        """
        self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                               "border-radius: 8px;\n"
                               "color: #000000")
        self.displayNumber.emit(self.value)
        self.setTarget.emit(f"set {self.target};")
        self.changing = False
        self.lock.unlock()
    
    def output(self, value):
        """METHOD: output
        
        Instructs the GUI to update the displayed value only if the display isn't doing something else already
        
        Called by:
            none
        
        Arguments:
            none
        
        Returns:
            none
        
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
            none
        
        Arguments:
            none
        
        Returns:
            float - The current target value
        """
        return self.target