import json
from PyQt5.QtCore import QObject, pyqtSignal, QRegularExpression
from PyQt5.QtWidgets import QWidget, QLabel, QDial, QRadioButton
from ringTool import Animation

#FUTURE: Create superclass for all NeoPixel tool classes
class PixelTool(QObject):
    """CLASS: PixelTool
    
    This class handles some of the interactions between the objects in a QToolBox pane for a NeoPixel and sends messages to the Metro Mini when settings change.
    
    SIGNALS                          SLOTS
    ------------------    ----------------
    sendToSerial (str)    (int) changeMode
                          ()  colorChanged
                          ()  sendNewColor
                          ()  sendNewCycle
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
    #FUTURE: Incorporate RingTool's Color enum (both would be moved to the superclass)
    def __init__(self, widget, serial, index):
        super().__init__()
        
        with open("styles.json") as file:
            self.styles = json.load(file)
            file.close()
        
        self.index = index
        self.modes = {Animation.STATIC: "static", Animation.BREATHE: "breathe", Animation.CYCLE: "cycle"}
        
        self.colorObjects = [self.identifyObjects(widget, ".*Red.*"), self.identifyObjects(widget, ".*Green.*"), self.identifyObjects(widget, ".*Blue.*")]
        self.square = widget.findChildren(QLabel, QRegularExpression("Color$"))[0]
        
        self.dial = widget.findChild(QDial)
        self.cycleLabel = widget.findChildren(QLabel, QRegularExpression("CYCLE$"))[0]
        self.dial.valueChanged.connect(lambda val: self.cycleLabel.setText(f"AnimAtion time: {max(val, 1)} sec"))
        self.dial.sliderReleased.connect(self.sendNewCycle)
        
        for obj in self.colorObjects:
            obj["slider"].valueChanged.connect(self.colorChanged)
            obj["slider"].sliderReleased.connect(self.sendNewColor)
        
        self.buttons = widget.findChildren(QRadioButton)[0].group()
        for b in self.buttons.buttons():
            if b.text() == "stAtic":
                self.buttons.setId(b, Animation.STATIC)
            elif b.text() == "BReAthe":
                self.buttons.setId(b, Animation.BREATHE)
            elif b.text() == "cycle":
                self.buttons.setId(b, Animation.CYCLE)
        self.buttons.idClicked.connect(self.changeMode)
        
        self.sendToSerial.connect(serial.broadcast)
        
    def initialize(self):
        """METHOD: initialize
                
        Sends initial settings to the Metro Mini by calling three slots as methods
                
        Called by:
            MainWindow.initializeSerialObjects
                
        Arguments:
            none
                
        Returns:
            none
        """
        self.sendNewColor()
        self.changeMode(self.buttons.checkedId())
    
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
        """SLOT: sendNewColor
                
        Compiles a string containing the new color of the pixel and sends it to the serial port
                
        Expects:
            none
                
        Connects to:
            QSlider.sliderReleased
        
        Emits:
            sendToSerial
        """
        self.sendToSerial.emit(f'pixel {self.index} {self.convertToHSV(self.colorObjects[0]["slider"].value(),self.colorObjects[1]["slider"].value(),self.colorObjects[2]["slider"].value())};')
    
    def colorChanged(self):
        """SLOT: colorChanged
                
        Calls updateSquare to avoid using it as a slot
                
        Expects:
            none
                
        Connects to:
            QSlider.valueChanged
        """
        self.updateSquare()
    
    def updateSquare(self, colorString = None):
        """METHOD: updateSquare
                
        Updates the color of the square indicating the current color, using the passed string if provided
        
        Arguments:
            str - An optional string representation of the color to be displayed
            
        Returns:
            none
        
        Called by:
            colorChanged, changeMode
        """
        if colorString is None:
            color = f'rgb({self.colorObjects[0]["slider"].value()},{self.colorObjects[1]["slider"].value()},{self.colorObjects[2]["slider"].value()})'
        else:
            color = colorString
        if color == "rgb(0,0,0)":
            color = "#ffffff"
            self.square.setText("off")
        else:
            self.square.clear()
        self.square.setStyleSheet("border: 2px solid #000000;\n"
                                  "color: #000000;\n"
                                  f"background-color: {color};")
        
    def sendNewCycle(self):
        """SLOT: sendNewCycle
    
        Checks a new cycle dial value to make sure it's valid and sends it to the Metro Mini
    
        Expects:
            none
    
        Connects to:
            QDial.sliderReleased
    
        Emits:
            sendToSerial
        """
        if self.dial.value() == 0:
            self.dial.setValue(1)
        if self.buttons.checkedId() != Animation.STATIC:
            self.sendToSerial.emit(f"pixel {self.index} " + self.modes[self.buttons.checkedId()] + f" {self.dial.value()};")
    
    def changeMode(self, mode):
        """SLOT: changeMode
                
        Sends a message to the serial port indicating a change in animation style
                
        Expects:
            int - The enum value of the new animation mode
                
        Connects to:
            QButtonGroup.idClicked
        
        Emits: sendToSerial
        """
        arg = ""
        if mode != Animation.STATIC:
            arg = f" {self.dial.value()}"
        notCycle = mode != Animation.CYCLE
        for obj in self.colorObjects:
            obj["slider"].setStyleSheet(self.styles["QSlider-" + str(notCycle)])
            obj["label"].setStyleSheet(self.styles["QLabel-" + str(notCycle)])
            obj["value"].setStyleSheet(self.styles["QLabel-" + str(notCycle)])
        if notCycle:
            self.updateSquare()
        else:
            self.updateSquare("qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 0, 0, 255), stop:0.166 rgba(255, 255, 0, 255), stop:0.333 rgba(0, 255, 0, 255), stop:0.5 rgba(0, 255, 255, 255), stop:0.666 rgba(0, 0, 255, 255), stop:0.833 rgba(255, 0, 255, 255), stop:1 rgba(255, 0, 0, 255))")
        self.sendToSerial.emit(f"pixel {self.index} {self.modes[mode]}{arg};")
    
    def convertToHSV(self, ri, gi, bi):
        """METHOD: convertToHSV
                
        Converts an RGB value to HSV before sending it to the Metro Mini
                
        Called by:
            sendNewColor, RingTool.revertColors
                
        Arguments:
            int, int, int - The red, green, and blue values of the color
                
        Returns:
            str - A string containing the hue, saturation, and value of the color
        """
        r, g, b = float(ri / 255.0), float(gi / 255.0), float(bi / 255.0)
        v = max(r, g, b)
        c = v - min(r, g, b)
        if c == 0:
            h = float(0)
        elif v == r:
            h = float(60.0 * ((g - b) / c))
        elif v == g:
            h = float(60.0 * (2.0 + (b - r) / c))
        elif v == b:
            h = float(60.0 * (4.0 + (r - g) / c))
        if v == 0:
            s = float(0)
        else:
            s = float(c / v)
        if h < 0:
            h += 360.0
        return f"{int(h * 65536 / 360)} {int(s * 255)} {int(v * 255)}"          