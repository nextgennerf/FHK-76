'''
Created on Apr 26, 2021

@author: Jeffrey Blum
'''
from things.ioModule import IOModule

class Indicator(IOModule):
    '''
    Class for indicators that only turn off and on
    '''


    def __init__(self, sim, initState = 0, arg3 = ["off", "on"]):
        '''
        Constructor
        '''
        super().__init__(sim)
        self.state = initState
        if self.simulated:
            self.states = arg3
        else:
            self.path = arg3
    
    def turnOn(self):
        if self.state:
            print("ERROR: " + self.name + " is already " + self.states[self.state])
        else:
            self.state = 1
            print(self.name + " is " + self.states[self.state])
    
    def turnOff(self):
        if self.state:
            self.state = 0
            print(self.name + " is " + self.states[self.state])
        else:
            print("ERROR: " + self.name + " is already " + self.states[self.state])