'''
Created on Apr 27, 2021

@author: Jeffrey Blum
'''

import threading, asyncio
from PyQt5.Qt import QObject, pyqtSignal

_DELAY = 1.0

class FeedbackDisplay(QObject):
    '''
    This class wraps a QLCDNumber in the GUI that needs to keep track of a target value.
    '''
    setTarget = pyqtSignal(int)

    def __init__(self, lcd, initVal, targetVal):
        '''
        Constructor
        '''
        self.lcd = lcd
        lcd.display(float(initVal))
        self.target = float(targetVal)
        self.changing = False
        self.timer = threading.Timer(_DELAY, self.reset)
    
    def getObject(self):
        return self.lcd
    
    def changeTarget(self, delta):
        self.changing = True
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
        self.timer = threading.Timer(_DELAY, lambda: self.finalize(self.lcd.value()))
        self.timer.start()
        
    def finalize(self, value):
        self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                               "border-radius: 8px;\n"
                               "color: #000000")
        self.changing = False
        self.setTarget.emit(self.target)
        self.lcd.display(value)
    
    async def update(self, value):
        while self.changing:
            await asyncio.sleep(1)
        self.lcd.display(value)
    
    def getTarget(self):
        return self.target