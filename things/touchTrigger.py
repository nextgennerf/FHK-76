from PyQt5.QtCore import pyqtSignal, QState, QStateMachine, QSignalTransition
from things.button import Button

class TouchTrigger(QStateMachine, Button):
    """CLASS: TouchTrigger
    
    This Button subclass adds the capacitive touch functionality of the main trigger using a state machine.
    
    SIGNALS              SLOTS
    -----------------    -----
    letGo          ()     none
    pressed        ()
    printStatus (str)
    QState.entered ()
    QState.exited  ()
    released       ()
    touched        ()
    """
    
    pressed = pyqtSignal()
    """SIGNAL: pressed (COPIED FROM BUTTON)
    
    Emitted when the button is pressed
    
    Broadcasts:
        none
    
    Connects to:
        (FHK76.safety) FHK76.setSafety, (FHK76.modeButtons[*]) QPushButton.click (MainWindow.modeButtons.button(*).click),
        (FHK76.trigger) TouchTrigger state transition (offState -> revState)
    """
        
    released = pyqtSignal()
    """SIGNAL: released (COPIED FROM BUTTON)
    
    Emitted when the button is released
    
    Broadcasts:
        none
    
    Connects to:
        (FHK76.safety) FHK76.releaseSafety, (FHK76.trigger) TouchTrigger state transition (onState -> revState)
    """
    
    touched = pyqtSignal()
    """SIGNAL: touched
            
    Emitted when the user touches the trigger
            
    Broadcasts:
        none
            
    Connects to:
        TouchTrigger state transition (offState -> revState)
    """
    
    letGo = pyqtSignal()
    """SIGNAL: letGo
            
    Emitted when the user takes their finger off the trigger
            
    Broadcasts:
        none
            
    Connects to:
        TouchTrigger state transition (revState -> offState)
    """
    
    printStatus = pyqtSignal(str)
    """SIGNAL: printStatus (COPIED FROM IOMODULE)
    
    Displays a temporary message on the simulator's status bar
    
    Broadcasts:
        str - The temporary message to display
    
    Connects to:
        QMainWindow.QStatusBar.showMessage (MainWindow.simulator)
    """

    def __init__(self, blaster, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offState = QState()
        self.revState = QState()
        self.onState = QState()
        
        for s in [self.offState, self.revState, self.onState]:
            self.addState(s)
        self.setInitialState(self.offState)
        
        self.offState.entered.connect(lambda: blaster.triggerStateChange(3))
        self.offState.exited.connect(lambda: blaster.triggerStateChange(0))
        self.onState.entered.connect(lambda: blaster.triggerStateChange(1))
        self.onState.exited.connect(lambda: blaster.triggerStateChange(2))
        
        self.spinUp = QSignalTransition(self.touched)
        self.spinUp.setTargetState(self.revState)
        self.spinDown = QSignalTransition(self.letGo)
        self.spinDown.setTargetState(self.offState)
        self.revState.addTransition(self.pressed, self.onState)
        self.onState.addTransition(self.released, self.revState)
        
        self.start()
    
    def enableTouch(self, en):
        """METHOD: enableTouch
                
        Enables or disables response to touch
                
        Called by:
            FHK76.setSafety, FHK76.releaseSafety
                
        Arguments:
            bool - Whether touch response should be enabled
                
        Returns:
            none
        """
        if en:
            self.offState.addTransition(self.spinUp)
            self.revState.addTransition(self.spinDown)
        else:
            if len(self.offState.transitions()) > 0: # No need to remove transitions before they've been added
                self.offState.removeTransition(self.spinUp)
            if len(self.revState.transitions()) > 1: # revState has two transitions whereas offState only has one
                self.revState.removeTransition(self.spinDown)