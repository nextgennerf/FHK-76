from things.motor import Motor

class ControlledMotor(Motor):
    """This Motor subclass represents a motor with speed control. It is currently under construction.
    """
    #TODO: finish building, add callers from FHK76

    def __init__(self, sim, pwmIn = 0.0, wake = False, en = False, err = False):
        super().__init__(sim, en, err)
        if pwmIn < 0.15:
            self.dutyCycle = 0
            self.err = False
        elif pwmIn > 85:
            self.dutyCycle = 100
        else:
            self.dutyCycle = int(10/7 * (pwmIn - 15))
        self.wake = wake
    
    def turnOn(self):
        if not self.wake:
            print(self.name + " cannot run because it is asleep")
        elif not self.en:
            print(self.name + " cannot run because it is disabled")
        elif self.err:
            print(self.name + " cannot run because there is an error")
        else:
            print(self.name + " is running with a duty cycle of " + self.dutyCycle + "%")
            
    def turnOff(self):
        print(self.name + " is stopped")
            
    def enable(self):
        self.en = True
        print(self.name + " is enabled")
        
    def disable(self):
        self.en = False
        print(self.name + " is disabled")
    
    def triggerError(self):
        self.err = True
        print(self.name + " has an error")
    
    def clearError(self):
        if self.err:
            self.err = False
            print(self.name + " error is cleared")
        else:
            print(self.name + " has no error")
    
    def setDutyCycle(self, dc):
        self.dc = dc
        print(self.name + " duty cycle is " + self.dutyCycle + "%")
    
    def wake(self):
        self.wake = True
        print(self.name + " is awake")
    
    def sleep(self):
        self.wake = False
        print(self.name + " is asleep")