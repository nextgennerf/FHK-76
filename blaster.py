'''
Created on Apr 26, 2021

@author: Jeffrey Blum
'''
from things.touchTrigger import TouchTrigger
from things.button import Button
from things.LEDbutton import LEDButton
from things.motor import Motor
from things.controlledMotor import ControlledMotor
from things.indicator import Indicator

class FHK76:
    '''
    Top-level class, represents the blaster as a whole
    '''
    
    def __init__(self, gui, fps, sim):
        '''
        Constructor needs a boolean to decide whether to create a real or fake blaster. The asyncio loop coordinates all input loops and triggers the
        appropriate outputs.
        '''
        
        mb = gui.getModeButtons()
        self.inputs = {"trigger":TouchTrigger(sim), "semi":LEDButton(sim, mb, 0), "burst":LEDButton(sim, mb, 1), "auto":LEDButton(sim, mb, 2),
                       "safety":Button(sim, initial_state = True, press_call = self.setSafety, release_call = self.releaseSafety)}
        self.mode = None
        self.fps = fps
        
        self.belt = Motor(sim)
        self.flywheels = [ControlledMotor(sim), ControlledMotor(sim)]
        self.safetyLED = Indicator(sim, False, ["red", "green"])
        self.laser = Indicator(sim)
        self.light = Indicator(sim)     
        if sim:
            self.nameSimulatedIO()
    
    '''
    Return the dictionary of inputs
    '''
    def getInputs(self):
        return self.inputs
    
    '''
    Change the color of the safety indicator to red
    '''
    def setSafety(self):
        self.safetyLED.turnOff()
    
    '''
    Change the color of the safety indicator to green
    '''
    def releaseSafety(self):
        self.safetyLED.turnOn()
    
    def toggleLight(self, on):
        self.light.turnOn() if on else self.light.turnOff()
    
    def toggleLaser(self, on):
        self.laser.turnOn() if on else self.laser.turnOff()
        
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
    Callback methods for the GUI (may delete after motor classes are finished)
    '''
    def changeMode(self, modeID):
        modes = ["semi","burst","auto"]
        if self.mode is not None:
            self.inputs[self.mode].turnOff()
        self.mode = modes[modeID]
        self.inputs[self.mode].turnOn()
        
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
        for i in list(self.inputs):
            self.inputs[i].connectSimulator(i, sim)
        