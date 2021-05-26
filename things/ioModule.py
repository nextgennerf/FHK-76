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
            self.printStatus.connect(lambda msg: self.simulator.statusBar().showMessage(msg, 5000))