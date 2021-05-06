from PyQt5.QtCore import pyqtSignal, QState, QStateMachine
from things.button import Button

class TouchTrigger(Button):
    """CLASS: TouchTrigger
    
    This Button subclass adds the capacitive touch functionality of the main trigger using a state machine.
    
    SIGNALS               SLOTS
    ------------------    -----
    Button.pressed  ()     none
    Button.released ()
    letGo           ()
    touched         ()
    """
    
    touched = pyqtSignal()
    """SIGNAL: touched
            
    Emitted when the user touches the trigger
            
    Broadcasts:
        none
            
    Connects to:
        TODO:
    """
    
    letGo = pyqtSignal()
    """SIGNAL: letGo
            
    Emitted when the user takes their finger off the trigger
            
    Broadcasts:
        none
            
    Connects to:
        TODO:
    """

    def __init__(self, sim, blaster):
        super().__init__(sim)
        self.stateLoop = QStateMachine()
        self.offState = QState()
        self.revState = QState()
        self.onState = QState()
        
        #TODO: connect blaster slots to state signals
        
        self.offState.addTransition(self, self.touched, self.revState)
        self.revState.addTransition(self, self.letGo, self.offState)
        self.revState.addTransition(self, self.pressed, self.onState)
        self.onState.addTransition(self, self.released, self.revState)
        
        for s in [self.offState, self.revState, self.onState]:
            self.stateLoop.addState(s)
        self.stateLoop.setInitialState(self.offState)
        self.stateLoop.start()