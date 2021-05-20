from PyQt5.QtCore import QObject, pyqtSignal

class IOModule(QObject):
    """CLASS: IOModule
    
    This superclass is inherited by all classes that represent physical inputs and outputs
    
    SIGNALS              SLOTS
    -----------------    -----
    printStatus (str)     none
    """
    
    printStatus = pyqtSignal(str)
    """SIGNAL: printStatus
            
    Displays a temporary message on the simulator's status bar
            
    Broadcasts:
        str - The temporary message to display
            
    Connects to:
        QMainWindow.QStatusBar.showMessage (MainWindow.simulator)
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.path, self.simulator = None, None
        if "path" in kwargs:
            self.path = kwargs["path"]
        if "simulator" in kwargs:
            self.simulator = kwargs["simulator"]
            self.printStatus.connect(lambda msg: self.simulator.statusBar().showMessage(msg, 10000))
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