from PyQt5.QtCore import pyqtSignal
from things.ioModule import IOModule

class Button(IOModule):
    """CLASS: Button
    
    This IO Module represents a button of any kind that can be pressed or released.
    
    SIGNALS        SLOTS
    -----------    -----
    pressed  ()     none
    released ()
    """
    
    pressed = pyqtSignal()
    """SIGNAL: pressed
    
    Emitted when the button is pressed
    
    Broadcasts:
        none
    
    Connects to:
        (FHK76.safety) FHK76.setSafety, (FHK76.modeButtons[*]) QPushButton.click (MainWindow.modeButtons.button(*).click),
        (FHK76.trigger) TouchTrigger state transition (offState -> revState)
    """
        
    released = pyqtSignal()
    """SIGNAL: released
    
    Emitted when the button is released
    
    Broadcasts:
        none
    
    Connects to:
        (FHK76.safety) FHK76.releaseSafety, (FHK76.trigger) TouchTrigger state transition (onState -> revState)
    """
    
    def __init__(self, sim):
        super().__init__(sim)