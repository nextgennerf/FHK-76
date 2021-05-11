from Simulator import Ui_Form
from things.state import State
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, QEvent

class Simulator(QWidget, Ui_Form):
    """CLASS: Simulator
    
    This class wraps the simulation window that helps test the code when it's not on the blaster.
    
    SIGNALS                                 SLOTS
    -----------------------    ------------------
    hover                ()    (int)  indicatorOn
    moveAway             ()    (int) indicatorOff
    QPushButton.pressed  ()    
    QPushButton.released ()
    """
    
    hover = pyqtSignal()
    """SIGNAL: hover
            
    Simulates touching the trigger
            
    Broadcasts:
        none
            
    Connects to:
        TouchTrigger.touched
    """
    
    moveAway = pyqtSignal()
    """SIGNAL: moveAway
            
    Simulates moving your finger away from the trigger
            
    Broadcasts:
        none
            
    Connects to:
        TouchTrigger.letGo
    """    

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buttons = {"semi":self.semiButton, "burst":self.burstButton, "auto":self.autoButton, "trigger":self.trigger, "safety":self.safety}
        self.indicators = {"safety":self.safetyLED, "laser":self.laserIndicator, "light":self.lightIndicator}
        self.trigger.installEventFilter(self)
    
    def eventFilter(self, event, *args, **kwargs):
        """METHOD: eventFilter
                
        Inherited method from QWidget for knowing when the mouse approaches and moves away from the trigger button
                
        Emits:
            hover, moveAway
        """
        if event.type() is QEvent.MouseMove:
            if self.trigger.underMouse():
                self.hover.emit()
            else:
                self.moveAway.emit()
    
    def printStatus(self, msg):
        """METHOD: printStatus
                
        Outputs a message to the status bar on the simulator
                
        Called by:
            indicatorOn, indicatorOff, IOModule.printStatus
                
        Arguments:
            str - The message to be displayed
                
        Returns:
            none
        """
        self.status.setText(msg)
            
    def getButton(self, name):
        """METHOD: getButton
                
        Access method for a button in the simulator
                
        Called by:
            FHK76.connectSimulator
                
        Arguments:
            str - the name of the requested button
                
        Returns:
            QPushButton - the requested button
        """
        if name in self.buttons:
            return self.buttons[name]
        else:
            self.status.setText("ERROR: Invalid button name passed to getButton()")
    
    def indicatorOn(self, num):
        """SLOT: indicatorOn
                
        Turns the simulator's indicators on
                
        Expects:
            int - the ID number of the indicator to be turned on
                
        Connects to:
            FHK76.turnOn
        """
        if num is 0:
            self.buttons["semi"].setStyleSheet("border: 5px solid #0000FF")
        elif num is 1:
            self.buttons["burst"].setStyleSheet("border: 5px solid #0000FF")
        elif num is 2:
            self.buttons["auto"].setStyleSheet("border: 5px solid #0000FF")
        elif num is 3:
            self.indicators["safety"].setText(State.ON)
        elif num is 4:
            self.indicators["light"].setText(State.ON)
        elif num is 5:
            self.indicators["laser"].setText(State.ON)
        else:
            self.printStatus("ERROR: Invalid indicator number passed to indicatorOn()")

    def indicatorOff(self, num):
        """SLOT: indicatorOff
                
        Turns the simulator's indicators off
                
        Expects:
            int - the ID number of the indicator to be turned off
                
        Connects to:
            FHK76.turnOff
        """
        if num is 0:
            self.buttons["semi"].setStyleSheet("")
        if num is 1:
            self.buttons["burst"].setStyleSheet("")
        if num is 2:
            self.buttons["auto"].setStyleSheet("")
        elif num is 3:
            self.indicators["safety"].setText(State.OFF)
        elif num is 4:
            self.indicators["light"].setText(State.OFF)
        elif num is 5:
            self.indicators["laser"].setText(State.OFF)
        else:
            self.printStatus("ERROR: Invalid indicator number passed to indicatorOff()")
    
    def getSerialOutput(self):
        """METHOD: getSerialOutput
                
        Access method for the QLabel that display messages sent over serial
                
        Called by:
            __main__
                
        Arguments:
            none
                
        Returns:
            QLabel - the output display
        """
        return self.serialSentMsg
    
    def getSerialInput(self):
        """METHOD: getSerialInput
                
        Access method for the QLabel that display messages received over serial
                
        Called by:
            __main__
                
        Arguments:
            none
                
        Returns:
            QLabel - the input display
        """
        return self.serialRcvdMsg