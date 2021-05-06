import asyncio
import concurrent.futures as cf
from PyQt5.QtCore import QObject, pyqtSignal

#TODO: Continue migrating to Qt

class TerminalSimulator(QObject):
    """CLASS: TerminalSimulator
    
    This non-blocking terminal call/response module simulates the blaster.
    
    SIGNALS                  SLOTS
    ---------------------    -----
    autoButtonPressed  ()     none
    burstButtonPressed ()
    safetyPressed      ()
    safetyReleased     ()
    semiButtonPressed  ()
    triggerTouched     ()
    """
    
    semiButtonPressed = pyqtSignal()
    """SIGNAL: semiButtonPressed
            
    Simulates pressing the semi-automatic fire button
            
    Broadcasts:
        none
            
    Connects to:
        QPushButton.click (MainWindow.semiButton)
    """
    
    burstButtonPressed = pyqtSignal()
    """SIGNAL: burstButtonPressed
            
    Simulates pressing the burst fire button
            
    Broadcasts:
        none
            
    Connects to:
        QPushButton.click (MainWindow.burstButton)
    """
    
    autoButtonPressed = pyqtSignal()
    """SIGNAL: autoButtonPressed
            
    Simulates pressing the automatic fire button
            
    Broadcasts:
        none
            
    Connects to:
        QPushButton.click (MainWindow.autoButton)
    """
    
    safetyPressed = pyqtSignal()
    """SIGNAL: safetyPressed
            
    Simulates switching on the safety
            
    Broadcasts:
        none
            
    Connects to:
        TODO:
    """
    
    safetyReleased = pyqtSignal()
    """SIGNAL: safetyReleased
            
    Simulates switching off the safety
            
    Broadcasts:
        none
            
    Connects to:
        TODO:
    """
    
    triggerTouched = pyqtSignal()
    """SIGNAL: triggerTouched
            
    Simulates touching the trigger
            
    Broadcasts:
        none
            
    Connects to:
        TODO:
    """

    def __init__(self, mb):
        super().__init__()
        self.semiButtonPressed.connect(mb.button(0).click)
        self.burstButtonPressed.connect(mb.button(1).click)
        self.autoButtonPressed.connect(mb.button(2).click)
    
    async def run(self):
        """METHOD: run
                
        Waits for and responds to user input through the terminal (asynchronous)
                
        Called by:
            __main__ (added as an asynchronous task)
                
        Arguments:
            none
                
        Returns:
            none
        
        Emits:
            autoButtonPressed, burstButtonPressed, semiButtonPressed
        """
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
                    #TODO: self.events["trigger press"].set()
                else:
                    #TODO: self.events[command].set()
            elif cWords[1] == "press":
                if cWords[0] == "semi":
                    self.semiButtonPressed.emit()
                elif cWords[0] == "burst":
                    self.burstButtonPressed.emit()
                elif cWords[0] == "auto":
                    self.autoButtonPressed.emit()
            elif command == "safety on":
                #TODO: self.events["safety press"].set()
            elif command == "safety off":
                #TODO: self.events["safety release"].set()
            else:
                print('Invalid command. To see a list of valid commands, enter "help".')