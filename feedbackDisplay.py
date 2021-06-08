from enum import Enum
from PyQt5.QtCore import QStateMachine, QState, QTimer, pyqtSignal

DELAY_BEFORE_SET = 1000 # Represents the time delay in milliseconds between the last GUI button press and the display returning to normal
REFRESH_PERIOD = 2000 # Represents the amount of time in milliseconds between sending data requests to the Metro Mini

class Color(Enum):
    """ENUM: Color
    
    Hex strings representing different display colors since that's all that changes in the style sheet
    """
    BLACK = "000000"
    GREEN = "00FF00"
    RED = "FF0000"

class DisplayState(QState):
    """CLASS: DisplayState
    
    This subclass of QState has additional functions to control the LCD display.
    
    SIGNALS                             SLOTS
    ----------------    ---------------------
    done          ()    (float) updateDisplay
    newValue (float)
    """
    
    #FUTURE: Figure out how to guarantee that four digits will be displayed.
    newValue = pyqtSignal(float)
    """SIGNAL: newValue
    
    Internal signal used to update the value displayed on the LCD
    
    Broadcasts:
        float - The new number to be displayed
    
    Connects to:
        QLCDNumber.display
    """
    
    done = pyqtSignal()
    """SIGNAL: done
    
    Internal signal used to trigger the transition to the waiting state
    
    Broadcasts:
        none
    
    Connects to:
        (FeedbackDisplay.upState, FeedbackDisplay.downState) FeedbackDisplay.stateMachine transition (* -> FeedbackDisplay.waitState)
    """
    
    def __init__(self, lcd, color, value = None):
        super().__init__()
        self.color = color.value
        self.lcd = lcd
        self.newValue.connect(lcd.display)
        self.value = value # The existence (i.e. not None) of this value is how you know the state cares about the actual value instead of the target value
    
    def onEntry(self, event):
        """METHOD: onEntry
                
        Superclass method override, automatically called when the state is entered
                
        Arguments:
            none
                
        Returns:
            none
        
        Emits:
            newValue, done
        """
        self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                               "border-radius: 8px;\n"
                               f"color: #{self.color}")
        dispVal = self.machine().getTarget() if self.value is None else self.value
        self.newValue.emit(dispVal)
        self.done.emit()
    
    def updateDisplay(self, newVal):
        """SLOT: updateDisplay
                
        Used to update the displayed and stored values at a time other than right when the state is entered
                
        Expects:
            float - The new value to display/store
                
        Connects to:
            (FeedbackState.defaultState) MetroMini.newDataAvailable [Connected by MainWindow]
        
        Emits:
            newValue
        """
        self.value = float(newVal)
        self.newValue.emit(self.value)

class FeedbackDisplay(QStateMachine):
    """CLASS: FeedbackDisplay
    
    This class wraps a QStateMachine and a QLCDNumber in the GUI so it can keep track of a target value and prevent competing display changes.
    
    SIGNALS                                 SLOTS
    ---------------------    --------------------
    lowerTarget        ()    (float) changeTarget
    raiseTarget        ()    ()       sendRequest
    sendToSerial    (str)    ()        sendTarget
    targetChanged (float)
    """
    
    targetChanged = pyqtSignal(float)
    """SIGNAL: targetChanged
    
    Emitted when the target value has changed
    
    Broadcasts:
        float - The new target value
    
    Connects to:
        TODO: (probably necessary for FPS)
    """
    
    raiseTarget = pyqtSignal()
    """SIGNAL: raiseTarget
            
    Internal state change signal
            
    Broadcasts:
        none
            
    Connects to:
        stateMachine transition (* -> upState)
    """
    
    lowerTarget = pyqtSignal()
    """SIGNAL: lowerTarget
            
    Internal state change signal
            
    Broadcasts:
        none
            
    Connects to:
        stateMachine transition (* -> downState)
    """
    
    sendToSerial = pyqtSignal(str)
    """SIGNAL: sendToSerial
            
    Delivers a message to be sent over serial
            
    Broadcasts:
        str - The message being sent
            
    Connects to:
        MetroMini.broadcast
    """

    def __init__(self, lcd, targetVal, serial = None, template = None):
        super().__init__()
        
        self.defaultState = DisplayState(lcd, Color.BLACK, 0.0)
        self.upState = DisplayState(lcd, Color.GREEN)
        self.downState = DisplayState(lcd, Color.RED)
        self.waitState = QState()
        
        self.setTimer = QTimer()
        self.setTimer.setInterval(DELAY_BEFORE_SET)
        self.setTimer.setSingleShot(True)
        self.waitState.entered.connect(self.setTimer.start)
        self.waitState.exited.connect(self.setTimer.stop)
        
        for s in [self.defaultState, self.upState, self.downState, self.waitState]:
            self.addState(s)
            s.addTransition(self.raiseTarget, self.upState)
            s.addTransition(self.lowerTarget, self.downState)
        for s in [self.upState, self.downState]:
            s.addTransition(s.done, self.waitState)
        self.waitState.addTransition(self.setTimer.timeout, self.defaultState)
        
        self.setInitialState(self.defaultState)
        
        self.target = float(targetVal)
        
        if serial is not None:
            #self.serial = serial
            self.template = template
            
            serial.newDataAvailable.connect(self.defaultState.updateDisplay)
            
            self.waitState.exited.connect(self.sendTarget)
            self.sendToSerial.connect(serial.broadcast)
            
            self.requestTimer = QTimer()
            self.requestTimer.setInterval(REFRESH_PERIOD)
            self.requestTimer.timeout.connect(self.sendRequest)
            self.defaultState.entered.connect(self.requestTimer.start)
            self.defaultState.exited.connect(self.requestTimer.stop)

        self.start()
    
    def getTarget(self):
        """METHOD: getTarget
    
        Access method for the current target value
    
        Called by:
            DisplayState.onEntry
    
        Arguments:
            none
    
        Returns:
            float - The current target value
        """
        return self.target
        
    def changeTarget(self, delta):
        """SLOT: changeTarget
    
        Applies a numeric change to the stored target value and directs the QLCDNumber to show that change.
    
        Expects:
            float: The amount by which to shift the target value
    
        Connects to:
            QPushButton.clicked (MainWindow.fpsUpButton, MainWindow.fpsDownButton, MainWindow.psiUpButton, MainWindow.psiDownButton)
            
        Emits:
            raiseTarget, lowerTarget, targetChanged
        """
        self.target += float(delta)
        if delta > 0:
            self.raiseTarget.emit()
        elif delta < 0:
            self.lowerTarget.emit()
        self.targetChanged.emit(self.target)
    
    def sendRequest(self):
        """SLOT: sendRequest
                
        Sends a serial message requesting a new value from the MetroMini. Eliminates the need for lambda.
                
        Expects:
            none
                
        Connects to:
            (MainWindow.psiDisplay) QTimer.timeout (requestTimer)
        
        Emits:
            sendToSerial
        """
        self.sendToSerial.emit("request;")
    
    def sendTarget(self):
        """SLOT: sendTarget
                
        Sends a serial message with a new target value to the MetroMini. Eliminates the need for lambda.
                
        Expects:
            none
                
        Connects to:
            (MainWindow.psiDisplay) QState.exited (waitState)
        
        Called by:
            MainWindow.initializeSerialObjects
        
        Emits:
            sendToSerial
        """
        self.sendToSerial.emit(self.template.format(self.target))