from PyQt5.QtCore import pyqtSignal
from things.ioModule import IOModule

class Button(IOModule):
    """CLASS: Button
    
    This IO Module represents a button of any kind that can be pressed or released.
    
    SIGNALS        SLOTS
    -----------    -----
    pressed  ()    
    released ()
    """
    
    pressed = pyqtSignal()
    """SIGNAL: pressed
    
    Emitted when the button is pressed
    
    Broadcasts:
        none
    
    Connects to:
        FHK76.setSafety
    """
        
    released = pyqtSignal()
    """SIGNAL: released
    
    Emitted when the button is released
    
    Broadcasts:
        none
    
    Connects to:
        FHK76.releaseSafety
    """
    
    def __init__(self, sim):
        super().__init__(sim)
    
    # def connectSimulator(self, name, sim):
    #     if self.simulated:
    #         self.name = name
    #         self.pressEvent = aio.Event()
    #         sim.addEvent(name + " press", self.pressEvent)
    #         self.releaseEvent = aio.Event()
    #         sim.addEvent(name + " release", self.releaseEvent)
            
    # async def loop(self):
    #     while True:
    #         if self.state:
    #             await self.releaseEvent.wait()
    #             self.state = False
    #             if self.simulated:
    #                 print(self.name + " released")
    #             if "release_call" in self.calls:
    #                 self.calls["release_call"]()
    #             self.releaseEvent.clear()
    #         else:
    #             await self.pressEvent.wait()
    #             self.state = True
    #             if self.simulated:
    #                 print(self.name + " pressed")
    #             if "press_call" in self.calls:
    #                 self.calls["press_call"]()
    #             self.pressEvent.clear()