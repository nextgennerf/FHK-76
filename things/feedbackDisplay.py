'''
Created on Apr 27, 2021

@author: Jeffrey Blum
'''

import threading

delay = 1.0

class FeedbackDisplay(object):
    '''
    This class wraps a QLCDNumber in the GUI that needs to keep track of a target value.
    '''


    def __init__(self, lcd, initVal, targetVal, uc = None):
        '''
        Constructor
        '''
        self.lcd = lcd
        lcd.display(float(initVal))
        self.target = float(targetVal)
        self.timer = threading.Timer(delay, self.reset)
        if uc is not None: #The PSI display needs to be able to forward its values on to the peripheral controller
            self.uc = uc
    
    def getObject(self):
        return self.lcd
    
    def changeTarget(self, delta):
        self.target += float(delta)
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
        self.timer = threading.Timer(delay, lambda: self.finalize(self.lcd.value()))
        self.timer.start()
        
    def finalize(self, value):
        self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                               "border-radius: 8px;\n"
                               "color: #000000")
        self.lcd.display(value)
        # if self.uc is not None:
        #     self.uc.setPSI(self.target)