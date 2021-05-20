from PyQt5.QtCore import pyqtSignal
from things.button import Button
from things.indicator import Indicator

class LEDButton(Indicator, Button):
    """CLASS: LEDButton
    
    This class inherits both Button and Indicator for a button that has an LED ring
    
    SIGNALS                          SLOTS
    ----------     -----------------------
    pressed  ()    (int) Indicator.turnOff
    released ()    (int) Indicator.turnOn
    """
    
    pressed = pyqtSignal()
    """SIGNAL: pressed (COPIED FROM BUTTON)
    
    Emitted when the button is pressed
    
    Broadcasts:
        none
    
    Connects to:
        (FHK76.safety) FHK76.setSafety, (FHK76.modeButtons[*]) QPushButton.click (MainWindow.modeButtons.button(*)), (FHK76.trigger) TouchTrigger state transition (offState -> revState)
    """
        
    released = pyqtSignal()
    """SIGNAL: released (COPIED FROM BUTTON)
    
    Emitted when the button is released
    
    Broadcasts:
        none
    
    Connects to:
        (FHK76.safety) FHK76.releaseSafety, (FHK76.trigger) TouchTrigger state transition (onState -> revState)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)