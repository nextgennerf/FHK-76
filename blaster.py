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
    
    SIGNALS                       SLOTS
    -------------    ------------------
    turnOff (int)    ()   releaseSafety
    turnOn  (int)    ()       setSafety
                     (bool) toggleLaser
                     (bool) toggleLight
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
    
    def __init__(self, mb, fps, sim):
        super().__init__()
        
        self.trigger = TouchTrigger(sim, self)
        
        self.safety = Button(sim)
        self.safety.pressed.connect(self.setSafety)
        self.safety.released.connect(self.releaseSafety)
        
        modes = ["semi", "burst", "auto"]
        self.modeButtons = {}
        for m in modes:
            i = modes.index(m)
            if sim is not None:
                l = LEDButton(i, simulator = sim)
            else:
                l = LEDButton(i)
            self.modeButtons[m] = l
            self.turnOn.connect(l.turnOn)
            self.turnOff.connect(l.turnOff)
            self.modeButtons[m].pressed.connect(mb.button(i).click)

        self.mode = None
        self.fps = fps
        
        # self.belt = Motor(sim)
        # self.flywheels = [ControlledMotor(sim), ControlledMotor(sim)]
        
        self.safetyLED = Indicator(3, simulator = sim)
        self.laser = Indicator(4, simulator = sim)
        self.light = Indicator(5, simulator = sim)
        
        for ind in [self.safetyLED, self.laser, self.light]:
            self.turnOn.connect(ind.turnOn)
            self.turnOff.connect(ind.turnOff)
        if sim is None:
            pass #TODO: check state of safety
        else:
            self.setSafety()
        self.turnOff.emit(4)
        self.turnOff.emit(5)
        
        if sim is not None:
            self.nameSimulatedIO()
            self.printStatus.connect(lambda msg: sim.statusBar().showMessage(msg, 10000))
    
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
        self.trigger.setEnable(False)
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
        self.trigger.setEnable(True)
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
        self.printStatus.emit(str(val))
    
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
    
    def nameSimulatedIO(self):
        """METHOD: nameSimulatedIO
                
        Passes display names to all of the blaster's I/O during simulation
                
        Called by:
            FHK76.__init__
                
        Arguments:
            none
                
        Returns:
            none
        """
        self.trigger.setName("Trigger")
        self.safety.setName("Safety")
        self.modeButtons["semi"].setName("Semi-automatic fire button")
        self.modeButtons["burst"].setName("Burst fire button")
        self.modeButtons["auto"].setName("Automatic fire button")
        # self.belt.setName("Belt motor")
        # self.flywheels[0].setName("Top flywheel motor")
        # self.flywheels[1].setName("Bottom flywheel motor")
        self.safetyLED.setName("Safety LED")
        self.light.setName("Flashlight")
        self.laser.setName("Laser")
    
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