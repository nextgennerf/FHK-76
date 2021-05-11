from things.button import Button
from things.indicator import Indicator

class LEDButton(Indicator, Button):
    """CLASS: LEDButton
    
    This class inherits both Button and Indicator for a button that has an LED ring
    
    SIGNALS                                 SLOTS
    ------------------    -----------------------
    Button.pressed  ()    (int) Indicator.turnOff
    Button.released ()    (int)  Indicator.turnOn
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)