from Simulator import Ui_Simulator
from things.state import State
from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtCore import pyqtSignal, QEvent

class Simulator(QMainWindow, Ui_Simulator):
    """CLASS: Simulator
    
    This class wraps the simulation window that helps test the code when it's not on the blaster.
    
    SIGNALS                                      SLOTS
    -----------------------    -----------------------
    displayMessage    (str)    (bool) emitSafetySignal
    hover                ()    (int)       indicatorOn
    moveAway             ()    (int)      indicatorOff
    QPushButton.pressed  ()    
    QPushButton.released ()
    safetySet            ()
    safetyReleased       ()
    """
    
    displayMessage = pyqtSignal(str)
    """SIGNAL: displayMessage
            
    An internal signal used to push a temporary message to the status bar
            
    Broadcasts:
        str - The temporary message to display
            
    Connects to:
        QStatusBar.showMessage
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
    
    safetySet = pyqtSignal()
    """SIGNAL: safetySet
            
    This signal along with safetyReleased is used in lieu of the safety button's normal methods since the simulator uses clicks
            
    Broadcasts:
        none
            
    Connects to:
        Button.pressed (FHK76.safety)
    """
    
    safetyReleased = pyqtSignal()
    """SIGNAL: safetyReleased
            
    This signal along with safetySet is used in lieu of the safety button's normal methods since the simulator uses clicks
            
    Broadcasts:
        none
            
    Connects to:
        Button.released (FHK76.safety)
    """

    def __init__(self, *args, **kwargs):
        super(Simulator, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.status_bar.addWidget(QLabel("READY"))
        self.displayMessage.connect(lambda msg: self.status_bar.showMessage(msg, 5000)) # Temporary messages show for 5 seconds
        self.buttons = {"semi":self.semiButton, "burst":self.burstButton, "auto":self.autoButton, "trigger":self.trigger, "safety":self.safetyButton}
        self.safetyButton.clicked.connect(self.emitSafetySignal)
        self.indicators = {"safety":self.safetyIndicator, "laser":self.laserIndicator, "light":self.lightIndicator}
        self.triggerTouched = False # Because mouse tracking happens in the main widget, you need to know whether movement outside the button matters
        self.centralwidget.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """METHOD: eventFilter
                
        Inherited method from QWidget for knowing when the mouse approaches and moves away from the trigger button
                
        Emits:
            hover, moveAway
        """
        if event.type() == QEvent.MouseMove:
            if self.trigger.underMouse():
                self.triggerTouched = True
                self.hover.emit()
            elif self.triggerTouched is True:
                self.triggerTouched = False
                self.moveAway.emit()
        return False
            
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
    
    def emitSafetySignal(self, on):
        """SLOT: emitSafetySignal
                
        Translates clicks of the simulator's safety button into the signals for setting and releasing the safety
                
        Expects:
            bool - whether the button is checked or not
                
        Connects to:
            Button.pressed (FHK76.safety), Button.released (FHK76.safety)
        """
        if on:
            self.safetySet.emit()
        else:
            self.safetyReleased.emit()
    
    def indicatorOn(self, num):
        """SLOT: indicatorOn
                
        Turns the simulator's indicators on
                
        Expects:
            int - the ID number of the indicator to be turned on
                
        Connects to:
            FHK76.turnOn
        """
        if num == 0:
            self.buttons["semi"].setStyleSheet("border: 5px solid #0000FF")
        elif num == 1:
            self.buttons["burst"].setStyleSheet("border: 5px solid #0000FF")
        elif num == 2:
            self.buttons["auto"].setStyleSheet("border: 5px solid #0000FF")
        elif num == 3:
            self.indicators["safety"].setText(State.ON.value)
        elif num == 4:
            self.indicators["light"].setText(State.ON.value)
        elif num == 5:
            self.indicators["laser"].setText(State.ON.value)
        else:
            self.displayMessage.emit("ERROR: Invalid indicator number passed to indicatorOn()")

    def indicatorOff(self, num):
        """SLOT: indicatorOff
                
        Turns the simulator's indicators off
                
        Expects:
            int - the ID number of the indicator to be turned off
                
        Connects to:
            FHK76.turnOff
        """
        if num == 0:
            self.buttons["semi"].setStyleSheet("")
        elif num == 1:
            self.buttons["burst"].setStyleSheet("")
        elif num == 2:
            self.buttons["auto"].setStyleSheet("")
        elif num == 3:
            self.indicators["safety"].setText(State.OFF.value)
        elif num == 4:
            self.indicators["light"].setText(State.OFF.value)
        elif num == 5:
            self.indicators["laser"].setText(State.OFF.value)
        else:
            self.displayMessage.emit("ERROR: Invalid indicator number passed to indicatorOff()")
    
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