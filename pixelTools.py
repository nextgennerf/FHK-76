from enum import IntEnum
from PyQt5.QtCore import QObject, pyqtSignal, QRegularExpression
from PyQt5.QtWidgets import QWidget, QLabel, QDial

class Animation(IntEnum):
    """ENUM: Animation
    
    Integers representing different animation modes
    """
    STATIC = 0
    BREATHE = 1
    CYCLE = 2

class PixelTool(QObject):
    """CLASS: PixelTool
    
    This class handles some of the interactions between the objects in a QToolBox pane for a NeoPixel and sends messages to the MetroMini when settings change.
    
    SIGNALS                                  SLOTS
    ------------------    ------------------------
    sendToSerial (str)    (int)         changeMode
                          (bool) changeSliderStyle
                          ()          sendNewColor
                          ()          sendNewCycle
                          ()          updateSquare
    """

    sendToSerial = pyqtSignal(str)
    """SIGNAL: sendToSerial
            
    Delivers a message to be sent over serial
            
    Broadcasts:
        str - The message being sent
            
    Connects to:
        MetroMini.broadcast
    """
    
    #TODO: Add argument for passing initial settings
    def __init__(self, widget, buttons, serial, pin):
        super().__init__()
        
        self.id = pin
        self.modes = {Animation.STATIC: "static", Animation.BREATHE: "breathe", Animation.CYCLE: "cycle"}
        
        self.colorObjects = {"red": self.identifyObjects(widget, "\w*Red\w*"), "green": self.identifyObjects(widget, "\w*Green\w*"), "blue": self.identifyObjects(widget, "\w*Blue\w*")}
        c = widget.findChildren(QLabel, QRegularExpression("Color$"))
        self.square = c[0]
        self.dial = widget.findChild(QDial)
        c = widget.findChildren(QLabel, QRegularExpression("CYCLE$"))
        self.cycleLabel = c[0]
        
        for objDict in self.colorObjects.keys():
            objDict["slider"].valueChanged.connect(self.changeDisplayColor)
            objDict["slider"].sliderReleased.connect(self.sendNewColor)
        
        self.buttons = buttons
        for b in self.buttons.buttons():
            if b.text() is "stAtic":
                self.buttons.setId(b, Animation.STATIC)
            elif b.text() is "BReAthe":
                self.buttons.setId(b, Animation.BREATHE)
            elif b.text() is "cycle":
                self.buttons.setId(b, Animation.CYCLE)
                b.toggled.connect(self.changeSliderStyle)
        self.buttons.idClicked.connect(self.changeMode)
        
        self.sendToSerial.connect(serial.broadcast)
        
        self.dial.valueChanged.connect(lambda val: self.cycleLabel.setText(f"cycle time: {val} sec"))
        self.dial.sliderReleased.connect(self.sendNewCycle)
    
    def initialize(self):
        """METHOD: initialize
                
        Sends initial settings to the MetroMini
                
        Called by:
            MainWindow.initializeSerialObjects
                
        Arguments:
            none
                
        Returns:
            none
        
        Emits:
            sendToSerial
        """
        pass #TODO
    
    def identifyObjects(self, widget, regex):
        """METHOD: identifyObjects
                
        Identifies objects using a regular expression and labels them in a dictionary
                
        Called by:
            __init__
                
        Arguments:
            QWidget - The widget containing the objects being identified
            str - The regular expression used to identify the objects
                
        Returns:
            dict - The identified and labeled objects
        """
        objects = {}
        children = widget.findChildren(QWidget, QRegularExpression(regex))
        for obj in children:
            if obj.inherits("QSlider"):
                objects["slider"] = obj
            elif obj.objectName().endswith("Label"):
                objects["label"] = obj
            elif obj.objectName().endswith("Value"):
                objects["value"] = obj
        return objects
    
    def sendNewColor(self):
        pass #TODO  

    def changeSliderStyle(self, en):
        """SLOT: changeSliderStyle
                
        Change the appearance of the color sliders when the animation changes to or from cycle mode.
                
        Expects:
            bool - Whether cycle mode is active
                
        Connects to:
            QRadioButton.toggled (buttons.button(Animation.CYCLE))
        """
        color = "d6d6d6" if en else "000000"
        handle = "#ffffff" if en else "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9313a0, stop:1 #2f133c)"
        for objDict in self.colorObjects.keys():
            for obj in objDict.keys():
                if obj.inherits("QSlider"):
                    obj.setStyleSheet("QSlider::groove:vertical {\n"
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
                else:
                    obj.setStyleSheet(f"color: #{color}")
        if en:
            self.updateSquare("qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 0, 0, 255), stop:0.166 rgba(255, 255, 0, 255), stop:0.333 rgba(0, 255, 0, 255), stop:0.5 rgba(0, 255, 255, 255), stop:0.666 rgba(0, 0, 255, 255), stop:0.833 rgba(255, 0, 255, 255), stop:1 rgba(255, 0, 0, 255))")
        else:
            self.updateSquare()
    
    def updateSquare(self, arg = None):
        """METHOD/SLOT: updateSquare
                
        Updates the color of the square indicating the current color, using the passed string if provided
                
        Called by:
            changeSliderStyle
        
        Arguments:
            str - An optional representation of the color to be displayed
        
        Expects:
            none
        
        Connects to:
            QSlider.valueChanged
        """
        if type(arg) is str: # If this function is passed a string argument, it should override the default case
            color = arg
        else:
            color = f'rgb({self.colorObjects["red"]["slider"].value()},{self.colorObjects["green"]["slider"].value()},{self.colorObjects["blue"]["slider"].value()})'
            if color is "rgb(0,0,0)":
                color = "#ffffff"
                self.square.setText("off")
            else:
                self.square.setText("")
        self.square.setStyleSheet("border: 2px solid #000000;\n"
                                  "color: #000000;\n"
                                  f"background-color: {color};")
        
    def sendNewCycle(self):
        """SLOT: sendNewCycle
    
        Checks a new cycle dial value to make sure it's valid and sends it to the MetroMini if it is
    
        Expects:
            none
    
        Connects to:
            QDial.valueChanged
    
        Emits:
            sendToSerial
        """
        if self.dial.value() == 0:
            self.dial.setValue(1)
        if self.buttons.checkedId() is not Animation.STATIC:
            self.sendToSerial.emit(f"pixel {self.id} {self.modes[self.buttons.checkedId()]} {self.dial.value()};")
    
    def changeMode(self, mode):
        """SLOT: changeMode
                
        TODO: description
                
        Expects:
            int - The enum value of the new animation mode
                
        Connects to:
            QButtonGroup.idClicked
        """
        pass #TODO