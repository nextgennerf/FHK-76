from PyQt5.QtCore import QObject

class IOModule(QObject):
    """CLASS: IOModule
    
    This superclass is inherited by all classes that represent physical inputs and outputs
    
    SIGNALS    SLOTS
    -------    -----
    none        none
    """
    
    def __init__(self, **kwargs):
        super().__init__()
        self.path, self.simulator = None, None
        if "path" in kwargs:
            self.path = kwargs["path"]
        if "simulator" in kwargs:
            self.simulator = kwargs["simulator"]
        self.name = None
    
    def setName(self, name):
        """METHOD: setName
        
        Stores a name string to be displayed in the terminal when the system is being simulated
        
        Called by:
            FHK76.nameSimulatedIO
        
        Arguments:
            str - The displayed name of the input or output
        
        Returns:
            none
        """
        if self.simulator is not None:
            self.name = name
    
    def printStatus(self, msg):
        if self.simulator is not None:
            self.simulator.printStatus(msg)