from things.button import Button
from things.indicator import Indicator

class LEDButton(Button, Indicator):
    """CLASS: LEDButton
    
    This class inherits both Button and Indicator for a button that has an LED ring
    
    SIGNALS                                 SLOTS
    ------------------    -----------------------
    Button.pressed  ()    (int) Indicator.turnOff
    Button.released ()    (int)  Indicator.turnOn
    """

    def __init__(self, sim, modeID):
        Button.__init__(self, sim)
        Indicator.__init__(self, sim, modeID)
        self.modeID = modeID