from things.ioModule import IOModule

class Indicator(IOModule):
    """CLASS: Indicator
    
    This IO Module represents an LED or other light-based output that can be turned on and off.
    
    SIGNALS            SLOTS
    -------    -------------
    none       (int) turnOff
               (int)  turnOn
    """

    def __init__(self, num, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num = num # all indicators receive turn on and turn off signals but only one can respond
            
    
    def turnOn(self, num):
        """SLOT: turnOn
        
        Turns the indicator on if the ID is a match
        
        Expects:
            int - the ID of the indicator to be turned on
        
        Connects to:
            FHK76.turnOn
        """
        #TODO: File manipulation
    
    def turnOff(self, num):
        """SLOT: turnOff
        
        Turns the indicator off if the ID is a match
        
        Expects:
            int - the ID of the indicator to be turned on
        
        Connects to:
            FHK76.turnOff
        """
        #TODO: File manipulation