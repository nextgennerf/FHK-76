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

import sys, os, json, enum
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread
from MainWindow import Ui_MainWindow
from FHKSimulator import Simulator
from blaster import FHK76
from metroMini import MetroMini
from feedbackDisplay import FeedbackDisplay

useSimulator = True

class Pixel(enum.Enum):
    """ENUM: Pixel
    
    Pin numbers for MetroMini pixels
    """
    FRONT = list(range(24))
    LEFT = 24
    RIGHT = 25

class MainWindow(QMainWindow, Ui_MainWindow):
    """CLASS: MainWindow
    
    This class wraps the UI translated into Python from mainwindow.ui and adds methods to interact with the rest of the blaster.
    
    SIGNALS                                             SLOTS
    ----------------------------    -------------------------
    QButtonGroup.idClicked (int)    (str)         changeColor
    QPushButton.clicked       ()    (QDial)       changeCycle
    QPushButton.toggled   (bool)    (int)  changeFrontSliders
    QSlider.valueChanged   (int)    (bool, str) changeSliders
    QThread.started           ()    (int)    updateBurstValue
    """
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        
        #TODO: Add LED settings to JSON
        if os.path.exists("settings.json"): # load settings from file
            with open("settings.json") as file:
                settings = json.load(file)
            file.close()
        else: # default settings 
            settings = {"fps":100, "psi":60, "burst":3}
        
        self.modeButtons.setId(self.semiButton, 0)
        self.modeButtons.setId(self.burstButton, 1)
        self.modeButtons.setId(self.autoButton, 2)
        
        #TODO: Add static and breathe modes
        #FUTURE: Allow for individual ring LEDs to cycle (may require GUI change)
        
        self.ringColors = ["rgb(0,0,0)"] * len(Pixel.FRONT.value)
        self.selectorDial.valueChanged.connect(self.changeFrontSliders)
        self.applyAllState = self.applyAllCheckBox.isChecked()
        
        self.leftDial.valueChanged.connect(lambda val: self.leftCYCLE.setText(f"cycle time: {val} sec"))
        self.leftDial.valueChanged.connect(lambda val: self.changeCycle(self.leftDial))
        self.rightDial.valueChanged.connect(lambda val: self.rightCYCLE.setText(f"cycle time: {val} sec"))
        self.leftDial.valueChanged.connect(lambda val: self.changeCycle(self.rightDial))
        self.rightDial.valueChanged.connect(lambda val: self.frontCYCLE.setText(f"cycle time: {val} sec"))
        self.frontDial.valueChanged.connect(lambda val: self.changeCycle(self.frontDial))
        
        self.leftCycleButton.toggled.connect(lambda en: self.changeSliders(en, "left"))
        self.rightCycleButton.toggled.connect(lambda en: self.changeSliders(en, "right"))
        self.frontCycleButton.toggled.connect(lambda en: self.changeSliders(en, "front"))
        
        for s in [self.leftRedSlider, self.leftGreenSlider, self.leftBlueSlider]:
            s.valueChanged.connect(lambda val: self.changeColor(Pixel.LEFT))
        for s in [self.rightRedSlider, self.rightGreenSlider, self.rightBlueSlider]:
            s.valueChanged.connect(lambda val: self.changeColor(Pixel.RIGHT))
        for s in [self.frontRedSlider, self.frontGreenSlider, self.frontBlueSlider]:
            s.valueChanged.connect(lambda val: self.changeColor(Pixel.FRONT))
        self.applyAllCheckBox.toggled.connect(lambda en: self.changeColor(Pixel.FRONT))

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
            QSlider.valueChanged (burstSlider)
        """
        self.burstButton.setText("BURST: " + str(val))
        self.blaster.setBurstValue(val)
        
    def changeCycle(self, dial):
        """SLOT: changeCycle
                
        Checks a new cycle dial value to make sure it's valid and sends it to the MetroMini if it is
                
        Expects:
            QDial - the dial being checked
                
        Connects to:
            QDial.valueChanged (leftDial, rightDial, frontDial)
        """
        if dial.value() == 0:
            dial.setValue(1) # This will resend the signal that connects to this slot
        else:
            pass
            #TODO: send to MetroMini
    
    def changeColor(self, pixel):
        """SLOT: changeColor
                
        Changes the color of an LED or group of LEDs and sends the appropriate command to the MetroMini
                
        Expects:
            Pixel - The LED (or group of LEDs) that will be changed
                
        Connects to:
            QSlider.valueChanged (leftRedSlider, leftGreenSlider, leftBlueSlider, rightRedSlider, rightGreenSlider, rightBlueSlider, frontRedSlider, frontGreenSlider, frontBlueSlider)
            QCheckBox.toggled (applyAllCheckBox)
        """
        if pixel is Pixel.LEFT:
            self.updateSquare(self.leftColor, f"rgb({self.leftRedSlider.value()},{self.leftGreenSlider.value()},{self.leftBlueSlider.value()})")
            #TODO: send to MetroMini
        elif pixel is Pixel.RIGHT:
            self.updateSquare(self.rightColor, f"rgb({self.rightRedSlider.value()},{self.rightGreenSlider.value()},{self.rightBlueSlider.value()})")
            #TODO: send to MetroMini
        elif pixel is Pixel.FRONT:
            newColor = f"rgb({self.frontRedSlider.value()},{self.frontGreenSlider.value()},{self.frontBlueSlider.value()})"
            self.updateSquare(self.frontColor, newColor)
            if self.applyAllCheckBox.isChecked():
                self.ringColors = [newColor] * len(Pixel.FRONT.value)
                #TODO: send to MetroMini
            else:
                self.ringColors[self.selectorDial.value()] = newColor
                #TODO: send to MetroMini
    
    def updateSquare(self, square, color):
        """METHOD: updateSquare
                
        Updates the color of a given color indication square
                
        Called by:
            changeColor
                
        Arguments:
            QLabel - The square to be updated
            str - A string represent the new color
                
        Returns:
            none
        """
        if color == "rgb(0,0,0)":
            color = "#ffffff"
            square.setText("off")
        else:
            square.setText("")
        square.setStyleSheet("border: 2px solid #000000;\n"
                             "color: #000000;\n"
                             f"background-color: {color};")
    
    def changeSliders(self, cycEn, zone):
        """SLOT: changeSliders
                
        Change the appearance of the color sliders and their associated labels to indicate whether or not they're enabled.
                
        Expects:
            bool - Whether or not cycle mode is active
            str - Represents which group of sliders is being updated
                
        Connects to:
            QRadioButton.toggled (leftCycleButton, rightCycleButton, frontCycleButton)
        """
        if cycEn:
            self.applyAllState = self.applyAllCheckBox.isChecked()
            self.applyAllCheckBox.setChecked(True)
        else:
            self.applyAllCheckBox.setChecked(self.applyAllState)
        color = "d6d6d6" if cycEn else "000000"
        handle = "#ffffff" if cycEn else "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9313a0, stop:1 #2f133c)"
        if cycEn:
            newColor = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 0, 0, 255), stop:0.166 rgba(255, 255, 0, 255), stop:0.333 rgba(0, 255, 0, 255), stop:0.5 rgba(0, 255, 255, 255), stop:0.666 rgba(0, 0, 255, 255), stop:0.833 rgba(255, 0, 255, 255), stop:1 rgba(255, 0, 0, 255))"
        if zone == "left":
            labels = [self.leftRED, self.leftRedValue, self.leftGREEN, self.leftGreenValue, self.leftBLUE, self.leftBlueValue]
            sliders = [self.leftRedSlider, self.leftGreenSlider, self.leftBlueSlider]
            square = self.leftColor
            if not cycEn:
                newColor = f"rgb({self.leftRedSlider.value()},{self.leftGreenSlider.value()},{self.leftBlueSlider.value()})"
        elif zone == "right":
            labels = [self.rightRED, self.rightRedValue, self.rightGREEN, self.rightGreenValue, self.rightBLUE, self.rightBlueValue]
            square = self.rightColor
            sliders = [self.rightRedSlider, self.rightGreenSlider, self.rightBlueSlider]
            if not cycEn:
                newColor = f"rgb({self.rightRedSlider.value()},{self.rightGreenSlider.value()},{self.rightBlueSlider.value()})"
        elif zone == "front":
            labels = [self.frontRED, self.frontRedValue, self.frontGREEN, self.frontGreenValue, self.frontBLUE, self.frontBlueValue]
            sliders = [self.frontRedSlider, self.frontGreenSlider, self.frontBlueSlider]
            square = self.frontColor
            if not cycEn:
                newColor = f"rgb({self.frontRedSlider.value()},{self.frontGreenSlider.value()},{self.frontBlueSlider.value()})"
        for l in labels:
            l.setStyleSheet(f"color: #{color}")
        for s in sliders:
            s.setStyleSheet("QSlider::groove:vertical {\n"
                            f"    border: 1px solid #{color};\n"
                            "    width: 4px;\n"
                            f"    background: #{color};\n"
                            "    margin: 5px;\n"
                            "}\n"
                            "\n"
                            "QSlider::handle:vertical {\n"
                            f"    background: {handle};\n"
                            f"    border: 1px solid #{color};\n"
                            "    height: 18px;\n"
                            "    margin: 2px -20px;\n"
                            "    border-radius: 3px;\n"
                            "}")
        self.updateSquare(square, newColor)
    
    def changeFrontSliders(self, num):
        """SLOT: changeFrontSliders
                
        Changes which front LED's color data is displayed
                
        Expects:
            int - The number of the active LED
                
        Connects to:
            QDial.valueChanged (selectorDial)
        """
        if num == 24:
            self.selectorDial.setValue(0)
        else:
            rgb = self.ringColors[num].split(",")
            r,g,b = int(rgb[0].strip("rgb(")),int(rgb[1]),int(rgb[2].strip(")"))
            self.frontRedSlider.setValue(r)
            self.frontGreenSlider.setValue(g)
            self.frontBlueSlider.setValue(b)
            self.updateSquare(self.frontColor, self.ringColors[num])
    
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