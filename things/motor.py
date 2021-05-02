'''
Created on Apr 25, 2021

@author: Jeffrey Blum
'''
from things.ioModule import IOModule

class Motor(IOModule):
    '''
    Base class for motor outputs
    '''

    def __init__(self, sim, en = None, err = None):
        '''
        Constructor
        '''
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