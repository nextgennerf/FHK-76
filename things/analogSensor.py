'''
Created on Apr 26, 2021

@author: Jeffrey Blum
'''
from things.ioModule import IOModule

class AnalogSensor(IOModule):
    '''
    Superclass for analog sensors
    '''


    def __init__(self, initVal, supply, sim):
        '''
        Constructor
        '''
        super().__init__(sim)
        self.vcc = supply
        self.value = initVal