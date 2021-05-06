''' 
Created on Apr 24, 2021

@author: Jeffrey Blum
'''
import asyncio
import concurrent.futures as cf
from PyQt5.QtCore import QObject, pyqtSignal

class TerminalSimulator(QObject):
    '''
    A terminal call/response module that simulates the blaster.
    '''
    semiButtonPressed = pyqtSignal()
    burstButtonPressed = pyqtSignal()
    autoButtonPressed = pyqtSignal()
    safetyPressed = pyqtSignal()
    safetyReleased = pyqtSignal()
    triggerTouched = pyqtSignal()

    def __init__(self, mb):
        '''
        Constructor
        '''
        super().__init__()
        self.semiButtonPressed.connect(mb.button(0).click)
        self.burstButtonPressed.connect(mb.button(1).click)
        self.autoButtonPressed.connect(mb.button(2).click)
        self.events = {}
    
    async def run(self):
        while True:
            loop = asyncio.get_running_loop()
            with cf.ThreadPoolExecutor() as pool:
                command = await loop.run_in_executor(pool, lambda: input(''))
            cWords = command.split()
            if command == "help":
                print("The following are valid commands, choosing one option from the brackets.")
                print("   trigger [touch, pull, relax, release]")
                print("   safety [on, off]")
                print("   [semi, burst, auto] press")
            elif cWords[0] == "trigger":
                if cWords[1] == "pull":
                    self.events["trigger press"].set()
                else:
                    self.events[command].set()
            elif cWords[1] == "press":
                if cWords[0] == "semi":
                    self.semiButtonPressed.emit()
                elif cWords[0] == "burst":
                    self.burstButtonPressed.emit()
                elif cWords[0] == "auto":
                    self.autoButtonPressed.emit()
            elif command == "safety on":
                self.events["safety press"].set()
            elif command == "safety off":
                self.events["safety release"].set()
            else:
                print('Invalid command. To see a list of valid commands, enter "help".')
    
    def addEvent(self, name, event):
        self.events[name] = event