'''
Created on Apr 27, 2021

@author: Jeffrey Blum
'''

import threading
from PyQt5.QtCore import QObject, pyqtSignal, QMutex

_DELAY = 1.0

class FeedbackDisplay(QObject):
    '''
    This class wraps a QLCDNumber in the GUI that needs to keep track of a target value.
    '''
    setTarget = pyqtSignal(str)
    displayNumber = pyqtSignal(float)

    def __init__(self, lcd, initVal, targetVal):
        '''
        Constructor
        '''
        super().__init__()
        self.lcd = lcd
        self.target = float(targetVal)
        self.changing = False
        self.timer = None
        self.lock = QMutex()
        self.displayNumber.connect(lcd.display)
        self.lcd.display(self.value)
        self.setTarget.emit(f"set {self.target};")
    
    def changeTarget(self, delta):
        if self.lock.tryLock():
            self.changing = True
        if self.changing:
            self.target += float(delta)
            if delta > 0:
                self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                                       "border-radius: 8px;\n"
                                       "color: #00FF00")
            elif delta < 0:
                self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                                       "border-radius: 8px;\n"
                                       "color: #FF0000")
            self.displayNumber.emit(self.target)
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(_DELAY, self.finalize)
            self.timer.start()
        
    def finalize(self):
        self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                               "border-radius: 8px;\n"
                               "color: #000000")
        self.lcd.display(self.value)
        self.setTarget.emit(f"set {self.target};")
        self.changing = False
        self.lock.unlock()
    
    def output(self, value):
        self.lock.lock()
        self.value = value
        self.displayNumber.emit(value)
        self.lock.unlock()
    
    def getTarget(self):
        return self.target