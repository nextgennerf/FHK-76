from PyQt5.QtCore import pyqtSignal, QState, QStateMachine
from things.button import Button

class TouchTrigger(QStateMachine, Button):
    """CLASS: TouchTrigger
    
    This Button subclass adds the capacitive touch functionality of the main trigger using a state machine.
    
    SIGNALS              SLOTS
    -----------------    -----
    pressed        ()     none
    released       ()
    letGo          ()
    QState.entered ()
    QState.exited  ()
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

    def __init__(self, sim, blaster):
        super().__init__(sim)
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
        
        self.offState.addTransition(self.touched, self.revState)
        self.revState.addTransition(self.letGo, self.offState)
        self.revState.addTransition(self.pressed, self.onState)
        self.onState.addTransition(self.released, self.revState)
        
        self.start()
    
    self.setEnable