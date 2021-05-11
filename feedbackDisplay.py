from enum import Enum
from PyQt5.QtCore import QObject, QStateMachine, QState, QTimer, pyqtSignal

_DELAY = 1000 # Represents the time delay in milliseconds between the last GUI button press and the display returning to normal

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
        self.color = color
        self.newValue.connect(lcd.display)
        self.value = value # The existence (i.e. not None) of this value is how you know the state cares about the actual value instead of the target value
    
    def onEntry(self):
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
            (FeedbackState.defaultState) MetroMini.newDataAvailable
        
        Emits:
            newValue
        """
        self.value = float(newVal)
        self.newValue.emit(self.value)

class FeedbackDisplay(QObject):
    """CLASS: FeedbackDisplay
    
    This class wraps a QStateMachine and a QLCDNumber in the GUI so it can keep track of a target value and prevent competing display changes.
    
    SIGNALS                                   SLOTS
    ---------------------    ----------------------
    messageReady    (str)    (float)   changeTarget
    targetChanged (float)    (float) composeMessage
    """
    
    messageReady = pyqtSignal(str)
    """SIGNAL: messageReady
    
    Emitted when a message is ready to be sent over serial
    
    Broadcasts:
        str - A message to be delivered to the peripheral controller
    
    Connects to:
        MetroMini.writeData
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

    def __init__(self, lcd, targetVal, serial = None, template = None):
        super().__init__()
        
        self.stateMachine = QStateMachine()
        self.defaultState = DisplayState(lcd, Color.BLACK, 0.0)
        self.upState = DisplayState(lcd, Color.GREEN)
        self.downState = DisplayState(lcd, Color.RED)
        self.waitState = QState()
        
        self.timer = QTimer()
        self.timer.setInterval(_DELAY)
        self.timer.setSingleShot(True)
        self.waitState.entered.connect(self.timer.start)
        self.waitState.exited.connect(self.timer.stop)
        
        for s in [self.defaultState, self.upState, self.downState, self.waitState]:
            self.stateMachine.addState(s)
        self.stateMachine.setInitialState(self.defaultState)

        for s in [self.defaultState, self.upState, self.downState, self.waitState]:
                s.addTransition(self, self.raiseTarget, self.upState)
                s.addTransition(self, self.lowerTarget, self.downState)
        for s in [self.upState, self.downState]:
            s.addTransition(s, s.done, self.waitState)
        self.waitState.addTransition(self.timer, self.timer.timeout(), self.defaultState)
        
        self.target = float(targetVal)
        if serial is not None:
            self.serial = serial
            self.template = template
            self.waitState.exited.connect(self.composeMessage)
    
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
    
    def getDefaultState(self):
        """METHOD: getDefaultState
                
        Access method for the default state, the only one that allows external setting of the displayed value
                
        Called by:
            MainWindow.__init__
                
        Arguments:
            none
                
        Returns:
            DisplayState - The state machine's default state
        """
        return self.defaultState
        
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
    
    def composeMessage(self):
        """SLOT: composeMessage
                
        If this display communicates with serial, this is triggered by the end of the wait state to compose the message to be sent.
                
        Expects:
            none
                
        Connects to:
            (waitState) QState.exited
        
        Emits:
            messageReady
        """
        self.messageReady.emit(self.template.format(self.target))