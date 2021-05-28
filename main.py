"""Created by Jeffrey Blum for Next Gen Nerf

This program executes on a BeagleBone Black to run the FHK-76 blaster.

Indicator Numbers are as follows:
0 - Semi-automatic fire selector button LED
1 - Burst fire selector button LED
2 - Automatic fire selector button LED
3 - Safety indicator LED
4 - Flashlight
5 - Laser
"""

import sys, os, json
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread
from MainWindow import Ui_MainWindow
from FHKSimulator import Simulator
from blaster import FHK76
from metroMini import MetroMini
from feedbackDisplay import FeedbackDisplay

useSimulator = True

class MainWindow(QMainWindow, Ui_MainWindow):
    """CLASS: MainWindow
    
    This class wraps the UI translated into Python from mainwindow.ui and adds methods to interact with the rest of the blaster.
    
    SIGNALS                                          SLOTS
    ----------------------------    ----------------------
    QButtonGroup.idClicked (int)    (int) updateBurstValue
    QPushButton.clicked       ()
    QPushButton.toggled   (bool)
    QSlider.valueChanged   (int)
    QThread.started           ()
    """
    
    def __init__(self, *args, **kwargs):
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

        self.thread = QThread()
        self.uc = MetroMini()
        self.uc.moveToThread(self.thread)
        self.thread.started.connect(self.uc.begin)
        
        self.simulator = None
        if useSimulator:
            self.simulator = Simulator()
            self.blaster = FHK76(self.modeButtons, settings["fps"], self.simulator)
            self.uc.connectSimulator(self.simulator)
            self.blaster.connectSimulator(self.simulator)
            self.simulator.show()
        else:
            self.blaster = FHK76(self.modeButtons, settings["fps"])
        
        self.fpsDisplay = FeedbackDisplay(self.fpsLCD, settings["fps"])
        self.psiDisplay = FeedbackDisplay(self.psiLCD, settings["psi"], self.uc, "set {0};")
        
        self.blaster.changeMode(self.modeButtons.checkedId())
        self.updateBurstValue(settings["burst"])
        
        self.modeButtons.idClicked.connect(self.blaster.changeMode)
        self.burstSlider.valueChanged.connect(self.updateBurstValue)
        
        self.thread.start()
        
        #FUTURE: Allow for finer control of target values
        self.FPSupButton.clicked.connect(lambda: self.fpsDisplay.changeTarget(5.0))
        self.FPSdownButton.clicked.connect(lambda: self.fpsDisplay.changeTarget(-5.0))
        self.PSIupButton.clicked.connect(lambda: self.psiDisplay.changeTarget(5.0))
        self.PSIdownButton.clicked.connect(lambda: self.psiDisplay.changeTarget(-5.0))
        
        self.lightButton.toggled.connect(self.blaster.toggleLight)
        self.laserButton.toggled.connect(self.blaster.toggleLaser)

    def updateBurstValue(self, val):
        """SLOT: updateBurstValue
                
        Changes the burst mode button's text and alerts the blaster when the burst size is changed
                
        Expects:
            int - The new burst size
                
        Connects to:
            QSlider.valueChanged
        """
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
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())