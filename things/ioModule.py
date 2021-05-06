from PyQt5.QtCore import QObject

class IOModule(QObject):
    """CLASS: IOModule
    
    This superclass is inherited by all classes that represent physical inputs and outputs
    
    SIGNALS    SLOTS
    -------    -----
    none        none
    """

    def __init__(self, sim):
        super().__init__()
        self.simulated = sim
        self.name = None 
    
    def setName(self, name):
        """METHOD: setName
        
        Stores a name string to be displayed in the terminal when the system is being simulated
        
        Called by:
            none
        
        Arguments:
            str: The displayed name of the input or output
        
        Returns:
            none
        
        Emits:
            none
        """
        if self.simulated:
            self.name = name