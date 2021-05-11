from PyQt5.QtCore import pyqtSignal, QState, QStateMachine, QObject
from things.button import Button

class TouchTrigger(QStateMachine, Button):
    """CLASS: TouchTrigger
    
    This Button subclass adds the capacitive touch functionality of the main trigger using a state machine.
    
    SIGNALS               SLOTS
    ------------------    -----
    Button.pressed  ()     none
    Button.released ()
    letGo           ()
    QState.entered  ()
    QState.exited   ()
    touched         ()
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
        
        self.offState.entered.connect(lambda: blaster.trigggerStateChange(0))
        self.offState.exited.connect(lambda: blaster.trigggerStateChange(1))
        self.onState.entered.connect(lambda: blaster.trigggerStateChange(2))
        self.onState.exited.connect(lambda: blaster.trigggerStateChange(3))
        
        self.offState.addTransition(self.touched, self.revState)
        self.revState.addTransition(self.letGo, self.offState)
        self.revState.addTransition(self.pressed, self.onState)
        self.onState.addTransition(self.released, self.revState)
        
        self.start()