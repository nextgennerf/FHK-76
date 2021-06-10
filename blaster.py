from PyQt5.QtCore import QObject, pyqtSignal
from things.touchTrigger import TouchTrigger
from things.button import Button
from things.LEDbutton import LEDButton
from things.motor import Motor
from things.controlledMotor import ControlledMotor
from things.indicator import Indicator

class FHK76(QObject):
    """CLASS: FHK76
    
    This class represents the FHK76 as whole, creating the I/O object and facilitating communication between them and the GUI as necessary
    
    SIGNALS                                 SLOTS
    -----------------    ------------------------
    printStatus (str)    (int)         changeMode
    turnOff     (int)    ()         releaseSafety
    turnOn      (int)    ()             setSafety
                         (bool)       toggleLaser
                         (bool)       toggleLight
                         (int) triggerStateChange
    """
    
    turnOn = pyqtSignal(int)
    """SIGNAL: turnOn
    
    Instructs a given indicator to turn on
    
    Broadcasts:
        int - The ID number of the indicator that should turn on
    
    Connects to:
        Indicator.turnOn
    """
    
    turnOff = pyqtSignal(int)
    """SIGNAL: pressed
    
    Instructs a given indicator to turn on.
    
    Broadcasts:
        int - The ID number of the indicator that should turn off
    
    Connects to:
        Indicator.turnOff
    """
    
    printStatus = pyqtSignal(str)
    """SIGNAL: printStatus (COPIED FROM IOMODULE)
            
    Displays a temporary message on the simulator's status bar
            
    Broadcasts:
        str - The temporary message to display
            
    Connects to:
        QMainWindow.QStatusBar.showMessage (MainWindow.simulator)
    """
    
    def __init__(self, mb, fps, sim = None):
        super().__init__()
        
        if sim is None:
            pass
        else:
            self.trigger = TouchTrigger(self, simulator = sim)
            self.safety = Button(simulator = sim)
            self.safetyLED = Indicator(3, simulator = sim)
            self.laser = Indicator(4, simulator = sim)
            self.light = Indicator(5, simulator = sim)
            self.printStatus.connect(lambda msg: sim.statusBar().showMessage(msg, 5000))
            
        self.safety.pressed.connect(self.setSafety)
        self.safety.released.connect(self.releaseSafety)
        
        modes = ["semi", "burst", "auto"]
        self.modeButtons = {}
        for m in modes:
            i = modes.index(m)
            if sim is None:
                l = LEDButton(i)
            else:
                l = LEDButton(i, simulator = sim)
            self.modeButtons[m] = l
            self.turnOn.connect(l.turnOn)
            self.turnOff.connect(l.turnOff)
            self.modeButtons[m].pressed.connect(mb.button(i).click)

        self.mode = None
        self.fps = fps
        
        # self.belt = Motor(sim)
        # self.flywheels = [ControlledMotor(sim), ControlledMotor(sim)]
        
        for ind in [self.safetyLED, self.laser, self.light]:
            self.turnOn.connect(ind.turnOn)
            self.turnOff.connect(ind.turnOff)
        if sim is None:
            pass #TODO: check state of safety
        else:
            self.setSafety()
        self.turnOff.emit(4)
        self.turnOff.emit(5)
    
    def setSafety(self):
        """SLOT: setSafety
        
        Turns the safety LED indicator green (blaster is safe)
        
        Expects:
            none
        
        Connects to:
            Button.pressed (FHK76.safety)
        
        Emits:
            turnOn
        """
        self.trigger.enableTouch(False)
        self.turnOn.emit(3)
    
    def releaseSafety(self):
        """SLOT: releaseSafety
        
        Turns the safety LED indicator red (blaster is able to fire)
        
        Expects:
            none
        
        Connects to:
            Button.released (FHK76.safety)
        
        Emits:
            turnOff
        """
        self.trigger.enableTouch(True)
        self.turnOff.emit(3)
    
    def toggleLight(self, on):
        """SLOT: toggleLight
        
        Changes the state of the flashlight
        
        Expects:
            bool - Whether the flashlight should be turned on
        
        Connects to:
            QPushButton.toggled (MainWindow.lightButton)
        
        Emits:
            turnOff, turnOn
        """
        self.turnOn.emit(4) if on else self.turnOff.emit(4)
    
    def toggleLaser(self, on):
        """SLOT: toggleLaser
        
        Changes the state of the laser
        
        Expects:
            bool - Whether the flashlight should be turned on
        
        Connects to:
            QPushButton.toggled (MainWindow.lightButton)
        
        Emits:
            turnOff, turnOn
        """
        self.turnOn.emit(5) if on else self.turnOff.emit(5)
      
    def triggerStateChange(self, val):
        """SLOT: triggerStateChange
        
        Coordinates the blaster's reaction to user interaction with the main trigger
        
        Expects:
            int - A number representing the state transition that occurred
        
        Connects to:
            QState.entered (TouchTrigger.onState, TouchTrigger.offState), QState.exited (TouchTrigger.onState, TouchTrigger.offState)
        """
        # if val == 0: #trigger is touched
        #     self.belt.turnOn()
        #     for f in self.flywheels:
        #         f.wake()
        # elif val == 1: #trigger is pulled
        #     for f in self.flywheels:
        #         f.turnOn()
        # elif val == 2: #trigger is released without removing finger
        #     for f in self.flywheels:
        #         f.turnOff()
        # elif val == 3: #finger is removed from trigger
        #     self.belt.turnOff()
        #     for f in self.flywheels:
        #         f.sleep()
        pass
    
    def changeMode(self, modeID):
        """SLOT: changeMode
        
        Changes the firing mode of the blaster
        
        Expects:
            int - A number representing the firing mode to be activated
        
        Connects to:
            MainWindow.QButtonGroup.idClicked
        """
        if self.mode is not None: # Don't throw an error the first time this is called
            self.turnOff.emit(self.mode)
        self.mode = modeID
        self.turnOn.emit(self.mode)
        
    def setBurstValue(self, val):
        """METHOD: setBurstValue
                
        Changes the number of rounds fired on every trigger pull in burst fire mode
                
        Called by:
            MainWindow.updateBurstValue
                
        Arguments:
            int - The number of rounds per burst
                
        Returns:
            none
        """
        self.burstValue = val
    
    def getBurstValue(self):
        """METHOD: getBurstValue
                
        Access method for the burst value
                
        Called by:
            MainWindow.closeEvent
                
        Arguments:
            none
                
        Returns:
            int - The current burst value
        """
        return self.burstValue
    
    def connectSimulator(self, sim):
        """METHOD: connectSimulator
                
        Connect the signals emitted by the terminal simulator to the appropriate slots
                
        Called by:
            __main__
                
        Arguments:
            Simulator - The simulator window to be connected
                
        Returns:
            none
        """
        for m in self.modeButtons.keys():
            sim.getButton(m).pressed.connect(self.modeButtons[m].pressed)
        sim.safetySet.connect(self.safety.pressed)
        sim.safetyReleased.connect(self.safety.released)
        sim.hover.connect(self.trigger.touched)
        sim.getButton("trigger").pressed.connect(self.trigger.pressed)
        sim.getButton("trigger").released.connect(self.trigger.released)
        sim.moveAway.connect(self.trigger.letGo)
        self.turnOn.connect(sim.indicatorOn)
        self.turnOff.connect(sim.indicatorOff)