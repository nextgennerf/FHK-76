from things.ioModule import IOModule

class Motor(IOModule):
    """This IO Module represents a motor. It is currently under construction.
    """
    #TODO: finish building

    def __init__(self, sim, en = None, err = None):
        super().__init__(sim)
        self.en = en
        self.error = err
    
    def turnOn(self):
        print(self.name + " is on")

    def turnOff(self):
        print(self.name + " is off")
            
    def enable(self):
        pass
        
    def disable(self):
        pass
    
    def triggerError(self):
        pass
    
    def clearError(self):
        pass