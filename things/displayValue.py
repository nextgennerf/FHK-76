'''
Created on Apr 27, 2021

@author: Jeffrey Blum
'''

import threading

delay = 1.0

class DisplayValue(object):
    '''
    This class wraps a value known to the blaster that is displayed with a QLCDNumber in the GUI
    '''


    def __init__(self, lcd, initVal, targetVal = None):
        '''
        Constructor
        '''
        self.lcd = lcd
        self.value = initVal
        self.target = targetVal
        self.timer = threading.Timer(delay, self.reset)
    
    def change(self, delta, target = False):
        if target:
            self.target += delta
            if delta > 0:
                self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                                       "border-radius: 8px;\n"
                                       "color: #00FF00")
            elif delta < 0:
                self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                                       "border-radius: 8px;\n"
                                       "color: #FF0000")
            self.lcd.display(self.target)
            self.timer.cancel()
            self.timer = threading.Timer(delay, self.reset)
            self.timer.start()
        else:
            self.value += delta
            self.lcd.display(self.value)
        
    def get(self):
        return self.value
    
    def set(self, val):
        self.value = val
    
    def reset(self):
        self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                               "border-radius: 8px;\n"
                               "color: #000000")
        self.lcd.display(self.value)