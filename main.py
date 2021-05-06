"""Created by Jeffrey Blum for Next Gen Nerf

This main file creates a wrapper around the translated GUI file with the methods needed to interact with the blaster.

Indicator Numbers are as follows:
0 - Semi-automatic fire selector button LED
1 - Burst fire selector button LED
2 - Automatic fire selector button LED
3 - Safety indicator LED
4 - Flashlight
5 - Laser
(((UPDATE blaster.py IF THIS CHANGES)))
"""

import sys, os, json
import asyncio as aio
from qasync import QEventLoop
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from MainWindow import Ui_MainWindow
from blaster import FHK76
from terminalSimulator import TerminalSimulator
from metroMini import MetroMini
from feedbackDisplay import FeedbackDisplay

useSimulator = True

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        
        if os.path.exists("settings.json"): # load settings from file
            with open("settings.json") as file:
                settings = json.load(file)
            file.close()
        else: # default settings 
            settings = {"fps":100, "psi":60, "burst":3}
        
        self.modeButtons.setId(self.semiButton, 0)
        self.modeButtons.setId(self.burstButton, 1)
        self.modeButtons.setId(self.autoButton, 2)
        self.modeButtons.idClicked.connect(self.blaster.changeMode)
        self.burstSlider.valueChanged.connect(self.updateBurstValue)
        
        self.blaster = FHK76(self.modeButtons, settings["fps"], useSimulator)
        self.blaster.changeMode(self.modeButtons.checkedId())
        self.updateBurstValue(settings[:"burst"])
        
        self.fpsDisplay = FeedbackDisplay(self.fpsLCD, settings["fps"])
        self.psiDisplay = FeedbackDisplay(self.psiLCD, settings["psi"])
        
        self.FPSupButton.clicked.connect(lambda: self.fpsDisplay.changeTarget(5))
        self.FPSdownButton.clicked.connect(lambda: self.fpsDisplay.changeTarget(-5))
        self.PSIupButton.clicked.connect(lambda: self.psiDisplay.changeTarget(5))
        self.PSIdownButton.clicked.connect(lambda: self.psiDisplay.changeTarget(-5))
        
        self.lightButton.toggled.connect(self.blaster.toggleLight)
        self.laserButton.toggled.connect(self.blaster.toggleLaser)
        
        self.thread = QThread()
        self.uc = MetroMini()
        self.uc.moveToThread(self.thread)
        self.thread.started.connect(self.uc.begin)
        self.psiDisplay.setTarget.connect(self.uc.writeData)
        self.uc.outputData.connect(self.psiDisplay.updateoutput)
        self.thread.start()
    
    def getBlaster(self):
        return self.blaster
    
    def getModeButtons(self):
        return self.modeButtons

    def updateBurstValue(self, val):
        self.burstButton.setText("BURST: " + str(val))
        self.blaster.setBurstValue(val)
    
    '''
    TODO: Figure out how to make sure this gets called during the shutdown routine
    '''
    def saveSettings(self):
        settings = {"fps":self.fps.getTarget(), "psi":self.psi.getTarget(), "burst":self.burstValue}
        with open('settings.json', 'w') as file:
            json.dump(settings,file,indent=2)
        file.close()
   
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    eLoop = QEventLoop(app)
    aio.set_event_loop(eLoop)
    
    with eLoop:
        window = MainWindow()
        window.show()
        i = window.getBlaster().getInputs()
        aio.create_task(i["trigger"].loop())
        aio.create_task(i["safety"].loop())
        if useSimulator:
            tSim = TerminalSimulator(window.getModeButtons())
            window.getBlaster().connectSimulator(tSim)
            aio.create_task(tSim.run())
        eLoop.run_forever()