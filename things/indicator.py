from things.ioModule import IOModule

class Indicator(IOModule):
    """CLASS: Indicator
    
    This IO Module represents an LED or other light-based output that can be turned on and off.
    
    SIGNALS            SLOTS
    -------    -------------
    none       (int)  turnOn
               (int) turnOff
    """

    def __init__(self, sim, num, initState = 0, arg3 = ["off", "on"]):
        super().__init__(sim)
        self.num = num # all indicators receive turn on and turn off signals but only one can respond
        self.state = initState
        if self.simulated:
            self.states = arg3
        else:
            self.path = arg3
    
    def turnOn(self, num):
        """SLOT: turnOn
        
        Turns the indicator on if the ID is a match
        
        Expects:
            int - the ID of the indicator to be turned on
        
        Connects to:
            none
        """
        if num == self.num:
            if self.simulated:
                if self.state:
                    print("ERROR: " + self.name + " is already " + self.states[self.state])
                else:
                    self.state = 1
                    print(self.name + " is " + self.states[self.state])
    
    def turnOff(self, num):
        """SLOT: turnOff
        
        Turns the indicator off if the ID is a match
        
        Expects:
            int - the ID of the indicator to be turned on
        
        Connects to:
            none
        """
        if self.num == num:
            if self.simulated:
                if self.state:
                    self.state = 0
                    print(self.name + " is " + self.states[self.state])
                else:
                    print("ERROR: " + self.name + " is already " + self.states[self.state])