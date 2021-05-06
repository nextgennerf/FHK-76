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
    
    SIGNALS          SLOTS
    -------------    -----
    turnOn  (int)     none
    turnOff (int)
    """
    
    turnOn = pyqtSignal(int)
    """SIGNAL: turnOn
    
    Instructs a given indicator to turn on
    
    Broadcasts:
        int - The ID number of the indicator that should turn on
    
    Connects to:
        Indicator.turnOn, LEDButton.turnOn
    """
    
    turnOff = pyqtSignal(int)
    """SIGNAL: pressed
    
    Instructs a given indicator to turn on.
    
    Broadcasts:
        int - The ID number of the indicator that should turn off
    
    Connects to:
        Indicator.turnOff, LEDButton.turnOff
    """
    
    def __init__(self, mb, fps, sim):
        super().__init__()
        
        self.trigger = TouchTrigger(sim)
        #TOSO: additional trigger signals
        
        self.safety = Button(sim)
        self.safety.pressed.connect(self.setSafety)
        self.safety.released.connect(self.releaseSafety)
        
        with ["semi", "burst", "auto"] as modes:
            for m in modes:
                i = modes.index[m]
                l = LEDButton(sim, i)
                self.modeButtons[m] = l
                self.turnOn.connect(l.turnOn)
                self.turnOff.connect(l.turnOff)
                #TODO: Button signal

        self.mode = None
        self.fps = fps
        
        self.belt = Motor(sim)
        self.flywheels = [ControlledMotor(sim), ControlledMotor(sim)]
        
        self.safetyLED = Indicator(sim, False, ["red", "green"])
        self.laser = Indicator(sim)
        self.light = Indicator(sim)        
        for ind in [self.safetyLED, self.laser, self.light]:
            self.turnOn.connect(ind.turnOn)
            self.turnOff.connect(ind.turnOff)
        
        if sim:
            self.nameSimulatedIO()
    
    def setSafety(self):
        """SLOT: setSafety
        
        Turns the safety LED indicator red (off)
        
        Expects:
            none
        
        Connects to:
            Button.pressed
        
        Emits:
            turnOff
        """
        self.turnOff.emit(3)
    
    def releaseSafety(self):
        """SLOT: releaseSafety
        
        Turns the safety LED indicator green (on)
        
        Expects:
            none
        
        Connects to:
            Button.released
        
        Emits:
            turnOn
        """
        self.turnOn.emit(3)
    
    def toggleLight(self, on):
        """SLOT: toggleLight
        
        Changes the state of the flashlight
        
        Expects:
            bool - Whether the flashlight should be turned on
        
        Connects to:
            none
        
        Emits:
            turnOff
        """
        self.turnOn.emit(4) if on else self.turnOff.emit(4)
    
    def toggleLaser(self, on):
        """SLOT: toggleLaser
        
        Changes the state of the laser
        
        Expects:
            bool - Whether the flashlight should be turned on
        
        Connects to:
            none
        
        Emits:
            turnOff
        """
        self.turnOn.emit(5) if on else self.turnOff.emit(5)
    
    #TODO: Continue comment creation here   
    '''
    User interactions with the primary trigger
    '''
    async def triggerAction(self, val):
        if val == 0: #trigger is touched
            self.belt.turnOn()
            for f in self.flywheels:
                f.wake()
        elif val == 1: #trigger is pulled
            for f in self.flywheels:
                f.turnOn()
        elif val == 2: #trigger is released without removing finger
            for f in self.flywheels:
                f.turnOff()
        elif val == 3: #finger is removed from trigger
            self.belt.turnOff()
            for f in self.flywheels:
                f.sleep()
    
    '''
    Slot methods for the GUI (may change after motor classes are finished)
    '''
    def changeMode(self, modeID):
        self.turnOff.emit(self.modeID)
        self.mode = modeID
        self.turnOn.emit(self.modeID)
        
    def setBurstValue(self, val):
        self.burstValue = val
    
    def setFPS(self, val):
        self.fps = val
    
    '''
    Provide display names for I/O if the blaster is being simulated
    '''
    def nameSimulatedIO(self):
        i = self.inputs
        i["trigger"].setName("Trigger")
        i["safety"].setName("Safety")
        i["semi"].setName("Semi-automatic fire button")
        i["burst"].setName("Burst fire button")
        i["auto"].setName("Automatic fire button")
        self.belt.setName("Belt motor")
        self.flywheels[0].setName("Top flywheel motor")
        self.flywheels[1].setName("Bottom flywheel motor")
        self.safetyLED.setName("Safety LED")
        self.light.setName("Flashlight")
        self.laser.setName("Laser")
            
    '''
    To preserve encapsulation when simulating, all inputs must be connected to the terminal.
    '''
    def connectSimulator(self, sim):
        self.inputs["trigger"].connectSimulator("trigger", sim)
        self.inputs["safety"].connectSimulator("safety", sim)