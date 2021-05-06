'''
Created on Apr 24, 2021

@author: Jeffrey Blum
'''
from things.button import Button
from things.indicator import Indicator

class LEDButton(Button, Indicator):
    '''
    Button subclass with LED ring
    '''

    def __init__(self, sim, modeID):
        Button.__init__(self, sim)
        Indicator.__init__(self, sim, modeID)
        self.modeID = modeID