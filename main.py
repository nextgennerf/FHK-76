'''
Created on Apr 24, 2021

@author: Jeffrey Blum

This main file creates a wrapper around the translated GUI file with the methods needed to interact with the blaster
'''
import sys, os, json
import asyncio as aio
from qasync import QEventLoop
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from MainWindow import Ui_MainWindow
from blaster import FHK76
from terminalSimulator import TerminalSimulator
from things.metroMini import MetroMini
from things.feedbackDisplay import FeedbackDisplay

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
        self.modeButtons.idClicked.connect(lambda modeID: self.blaster.changeMode(modeID))
        self.burstSlider.valueChanged.connect(lambda value: self.updateBurstValue(value))
        
        self.thread = QThread()
        self.uc = MetroMini()
        self.uc.moveToThread(self.thread)
        self.thread.started.connect(self.uc.begin)
        self.blaster.getPSI().setTarget.connect(self.uc.writeData)
        self.uc.outputData.connect(self.blaster.getPSI().updateoutput)
        self.thread.start()
        
        self.blaster = FHK76(self, [self.fpsLCD, self.psiLCD], useSimulator)
        self.blaster.changeMode(self.modeButtons.checkedId())
        
        self.FPSupButton.clicked.connect(lambda: self.blaster.getFPS().changeTarget(5))
        self.FPSdownButton.clicked.connect(lambda: self.blaster.getFPS().changeTarget(-5))
        self.PSIupButton.clicked.connect(lambda: self.blaster.getPSI().changeTarget(5))
        self.PSIdownButton.clicked.connect(lambda: self.blaster.getPSI().changeTarget(-5))

        self.lightButton.toggled.connect(lambda checked: self.blaster.toggleLight(checked))
        self.laserButton.toggled.connect(lambda checked: self.blaster.toggleLaser(checked))
    
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
        if self.uc is None:
            path = None
        else:
            path = self.uc.getPath()
        settings = {"fps":self.fps.getTarget(), "psi":self.psi.getTarget(), "burst":self.burstValue, "path":path}
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
        for i in window.getBlaster().getInputs().values():
            aio.create_task(i.loop())
        if useSimulator:
            tSim = TerminalSimulator()
            window.getBlaster().connectSimulator(tSim)
            aio.create_task(tSim.run())
        eLoop.run_forever()