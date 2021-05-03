'''
Created on Apr 24, 2021

@author: Jeffrey Blum

This main file creates a wrapper around the translated GUI file with the methods needed to interact with the blaster
'''
import sys
import asyncio as aio
from qasync import QEventLoop
from PyQt5 import QtWidgets
from MainWindow import Ui_MainWindow
from blaster import FHK76
from terminalSimulator import TerminalSimulator

useSimulator = True

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        
        self.modeButtons.setId(self.semiButton, 0)
        self.modeButtons.setId(self.burstButton, 1)
        self.modeButtons.setId(self.autoButton, 2)
        self.modeButtons.idClicked.connect(lambda modeID: self.blaster.changeMode(modeID))
        self.burstSlider.valueChanged.connect(lambda value: self.updateBurstValue(value))
        
        self.blaster = FHK76(self, [self.fpsLCD, self.psiLCD], useSimulator)
        self.blaster.changeMode(self.modeButtons.checkedId())
        
        self.FPSupButton.clicked.connect(lambda: self.blaster.getFPS().changeTarget(5, True))
        self.FPSdownButton.clicked.connect(lambda: self.blaster.getFPS().changeTarget(-5, True))
        self.PSIupButton.clicked.connect(lambda: self.blaster.getPSI().changeTarget(5, True))
        self.PSIdownButton.clicked.connect(lambda: self.blaster.getPSI().changeTarget(-5, True))

        self.lightButton.toggled.connect(lambda checked: self.blaster.toggleLight(checked))
        self.laserButton.toggled.connect(lambda checked: self.blaster.toggleLaser(checked))
    
    def getBlaster(self):
        return self.blaster
    
    def getModeButtons(self):
        return self.modeButtons

    def updateBurstValue(self, val):
        self.burstButton.setText("BURST: " + str(val))
        self.blaster.setBurstValue(val)
   
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