from enum import IntEnum
from PyQt5.QtCore import QObject, pyqtSignal, QRegularExpression
from PyQt5.QtWidgets import QWidget, QLabel, QDial, QCheckBox, QPushButton

class Animation(IntEnum):
    """ENUM: Animation
    
    Integers representing different animation modes
    """
    STATIC = 0
    BREATHE = 1
    CYCLE = 2

#FUTURE: Combine overridden methods that only change the serial message
class PixelTool(QObject):
    """CLASS: PixelTool
    
    This class handles some of the interactions between the objects in a QToolBox pane for a NeoPixel and sends messages to the MetroMini when settings change.
    
    NOTE: The initialize method calls almost every slot as a function. The one it does not call, updateSquare, is called as a function by changeSliderStyle.
    
    SIGNALS                                  SLOTS
    ------------------    ------------------------
    sendToSerial (str)    (int)         changeMode
                          (bool) changeSliderStyle
                          ()          sendNewColor
                          ()         sendNewCycle
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
        
        self.pin = pin
        self.modes = {Animation.STATIC: "static", Animation.BREATHE: "breathe", Animation.CYCLE: "cycle"}
        
        self.colorObjects = [self.identifyObjects(widget, ".*Red.*"), self.identifyObjects(widget, ".*Green.*"), self.identifyObjects(widget, ".*Blue.*")]
        c = widget.findChildren(QLabel, QRegularExpression("Color$"))
        self.square = c[0]
        
        self.dial = widget.findChild(QDial)
        c = widget.findChildren(QLabel, QRegularExpression("CYCLE$"))
        self.cycleLabel = None
        if len(c) > 0: # The RingTool subclass won't find anything
            self.cycleLabel = c[0]
        
        for obj in self.colorObjects:
            obj["slider"].valueChanged.connect(self.updateSquare)
            obj["slider"].sliderReleased.connect(self.sendNewColor)
        
        self.buttons = buttons
        for b in self.buttons.buttons():
            if b.text() == "stAtic":
                self.buttons.setId(b, Animation.STATIC)
            elif b.text() == "BReAthe":
                self.buttons.setId(b, Animation.BREATHE)
            elif b.text() == "cycle":
                self.buttons.setId(b, Animation.CYCLE)
                b.toggled.connect(self.changeSliderStyle)
        self.buttons.idClicked.connect(self.changeMode)
        
        self.sendToSerial.connect(serial.broadcast)
    
    def initialize(self):
        """METHOD: initialize
                
        Sends initial settings to the MetroMini
                
        Called by:
            MainWindow.initializeSerialObjects
                
        Arguments:
            none
                
        Returns:
            none
        """
        #These two signals can only be connected after the constructor is fully complete so they work properly in subclasses
        self.dial.valueChanged.connect(lambda val: self.cycleLabel.setText(f"cycle time: {max(val, 1)} sec"))
        self.dial.sliderReleased.connect(self.sendNewCycle)
        
        buttonList = self.buttons.buttons()
        self.changeSliderStyle(buttonList[Animation.CYCLE].isChecked())
        
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
        self.sendToSerial.emit(f'pixel {self.pin} {self.colorObjects[0]["slider"].value()} {self.colorObjects[1]["slider"].value()} {self.colorObjects[2]["slider"].value()};')

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
        for obj in self.colorObjects:
            obj["slider"].setStyleSheet("QSlider::groove:vertical {\n"
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
            obj["label"].setStyleSheet(f"color: #{color}")
            obj["value"].setStyleSheet(f"color: #{color}")
        if en:
            self.updateSquare("qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 0, 0, 255), stop:0.166 rgba(255, 255, 0, 255), stop:0.333 rgba(0, 255, 0, 255), stop:0.5 rgba(0, 255, 255, 255), stop:0.666 rgba(0, 0, 255, 255), stop:0.833 rgba(255, 0, 255, 255), stop:1 rgba(255, 0, 0, 255))")
        else:
            self.updateSquare()
    
    def updateSquare(self, arg = None):
        """SLOT: updateSquare
                
        Updates the color of the square indicating the current color, using the passed string if provided
        
        Expects:
            none
        
        Connects to:
            QSlider.valueChanged
        
        Arguments:
            str - An optional representation of the color to be displayed
        """
        if type(arg) is str: # If this function is passed a string argument, it should override the default case
            color = arg
        else:
            color = f'rgb({self.colorObjects[0]["slider"].value()},{self.colorObjects[1]["slider"].value()},{self.colorObjects[2]["slider"].value()})'
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
    
        Checks a new cycle dial value to make sure it's valid and sends it to the MetroMini
    
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
            self.sendToSerial.emit(f"pixel {self.pin} " + self.modes[self.buttons.checkedId()] + f" {self.dial.value()};")
    
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
        self.sendToSerial.emit(f"pixel {self.pin} {self.modes[mode]}{arg};")

class RingTool(PixelTool):
    """CLASS: RingTool
    
    This class handles some of the interactions between the objects in a pair of QToolBox panes for a ring of NeoPixels and sends messages to the MetroMini when settings change.
    
    NOTE: The initialize method calls almost every slot as a function. Of the ones it does not call, updateSquare is called as a function by changeSliderStyle from the superclass and
    changePixel is called by revertColors.
    
    SIGNALS                                SLOTS
    ------------------    ----------------------
    sendToSerial (str)    (bool) changeDirection
                          (int)       changeMode
                          (int)      changePixel
                          (bool)  enableRotation
                          (bool)    revertColors
                          ()        sendNewColor
                          ()     sendNewRotation
    """
    
    sendToSerial = pyqtSignal(str)
    """SIGNAL: sendToSerial (COPIED FROM PIXELTOOL)
            
    Delivers a message to be sent over serial
    
    Broadcasts:
        str - The message being sent
            
    Connects to:
        MetroMini.broadcast
    """
    
    #TODO: Add argument for passing initial settings
    def __init__(self, colorWidget, animationWidget, buttons, serial, startPin, length):
        super().__init__(colorWidget, buttons, serial, startPin)
        
        self.locationOffset = 0 # Since I cannot control which LED is where, this will allow me to shift the dial values to real locations.
        self.colors = [[0, 0, 0]] * length
        
        self.selectDial = self.dial # The dial found by the superclass constructor is not the right one for mode selection
        self.selectDial.valueChanged.connect(self.changePixel)
        
        self.applyAll = colorWidget.findChild(QCheckBox)
        self.applyAll.toggled.connect(self.revertColors)
        
        dials = animationWidget.findChildren(QDial)
        for d in dials:
            if d.objectName().startswith("rotate"):
                self.rotateDial = d
            else:
                self.dial = d
        cycles = animationWidget.findChildren(QLabel, QRegularExpression("CYCLE$")) # There are two of these in a RingTool
        for c in cycles:
            if c.objectName().startswith("rotate"):
                self.rotateLabel = c
            else:
                self.cycleLabel = c
        
        self.rotation = animationWidget.findChild(QCheckBox)        
        cw = animationWidget.findChildren(QPushButton, QRegularExpression(".*[^C]CW$"))
        self.direction = cw[0].group()
        self.clockwise = cw[0].isChecked()
        cw[0].toggled.connect(self.changeDirection)
        self.rotation.toggled.connect(self.enableRotation)
        self.rotation.toggled.connect(self.sendNewRotation)
        self.rotateDial.valueChanged.connect(lambda val: self.rotateLabel.setText(f"RotAtion time: {float((val + 1) / 2)} sec"))
        self.rotateDial.sliderReleased.connect(self.sendNewRotation)
        
        self.sendToSerial.connect(serial.broadcast)
        
        self.dial.valueChanged.connect(lambda val: self.cycleLabel.setText(f"cycle time: {max(val, 1)} sec"))
        self.dial.sliderReleased.connect(self.sendNewCycle)

    def initialize(self):
        """METHOD: initialize (OVERRIDES PIXELTOOL)
                
        Sends initial settings to the MetroMini
                
        Called by:
            MainWindow.initializeSerialObjects
                
        Arguments:
            none
                
        Returns:
            none
        """
        buttonList = self.buttons.buttons()
        self.changeSliderStyle(buttonList[Animation.CYCLE].isChecked())
        
        if self.applyAll.isChecked():
            self.sendNewColor()
        else:
            self.revertColors(False)
        
        self.changeMode(self.buttons.checkedId())
        self.enableRotation(self.rotation.isChecked())
    
    def sendNewColor(self):
        """SLOT: sendNewColor (OVERRIDES PIXEL TOOL)
                
        Compiles a string containing the new color of a pixel or the ring and sends it to the serial port
                
        Expects:
            none
                
        Connects to:
            QSlider.sliderReleased
        
        Emits:
            sendToSerial
        """
        if self.applyAll.isChecked():
            self.sendToSerial.emit(f'ring {self.colorObjects[0]["slider"].value()} {self.colorObjects[1]["slider"].value()} {self.colorObjects[2]["slider"].value()};')
        else:
            pin = (self.selectDial.value() + self.locationOffset) % len(self.colors)
            self.colors[pin] = [self.colorObjects[0]["slider"].value(), self.colorObjects[1]["slider"].value(), self.colorObjects[2]["slider"].value()]
            self.sendToSerial.emit(f"pixel {pin} {self.colors[pin][0]} {self.colors[pin][1]} {self.colors[pin][2]};")
        
    def sendNewRotation(self):
        """SLOT: sendNewRotation
    
        Sends a new rotation timing command to the serial port
    
        Expects:
            none
    
        Connects to:
            QDial.sliderReleased (rotateDial), QCheckBox.toggled (rotation)
    
        Emits:
            sendToSerial
        """
        if self.rotation.isChecked():
            if self.clockwise:
                dirString = "cw "
            else:
                dirString = "ccw "
            self.sendToSerial.emit("ring rotate " + dirString + str(float((self.rotateDial.value() + 1) / 2)) + ";")
        else:
            self.sendToSerial.emit("ring rotate off;")
    
    def changeMode(self, mode):
        """SLOT: changeMode (OVERRIDES PIXELTOOL)
                
        Sends a message to the serial port indicating a change in animation style
                
        Expects:
            int - The enum value of the new animation mode
                
        Connects to:
            QButtonGroup.idClicked
        
        Emits: sendToSerial
        """
        arg = ""
        if mode is not Animation.STATIC:
            arg = f" {self.dial.value()}"
        self.sendToSerial.emit(f"ring {self.modes[mode]}{arg};")
        
    def changePixel(self, pin):
        """SLOT: changePixel
                
        Change which pixel's RGB values are displayed in the menu
                
        Expects:
            int - The pin number of the pixel to be displayed
                
        Connects to:
            QDial.valueChanged (selectDial)
        """
        if pin == 24:
            pin = 0
        for n in range(3):
            self.colorObjects[n]["slider"].setValue(self.colors[(pin + len(self.colors) - self.locationOffset) % len(self.colors)][n])
    
    def revertColors(self, applyAllState):
        """SLOT: revertColors
                
        Revert all ring LEDs to their stored colors when the apply all box is unchecked or to the current color setting when it is checked
                
        Expects:
            bool - New state of the apply all box
                
        Connects to:
            QCheckBox.toggled (applyAll)
        """
        if applyAllState:
            self.sendToSerial.emit(f'ring {self.colorObjects[0]["slider"].value()} {self.colorObjects[1]["slider"].value()} {self.colorObjects[2]["slider"].value()};')
        else:
            self.changePixel(self.selectDial.value())
            for pin in range(len(self.colors)):
                self.sendToSerial.emit(f"pixel {pin} {self.colors[pin][0]} {self.colors[pin][1]} {self.colors[pin][2]};")
    
    def enableRotation(self, en):
        """SLOT: enableRotation
                
        Change the appearance of the rotation direction buttons when rotation is enabled or disabled
        
        Expects:
            bool - Whether rotation is enabled
                
        Connects to:
            QCheckBox.toggled (rotation)
        """
        style = "QPushButton {\n    border: 3px solid #61136E;\n    border-radius: 8px;\n    background-color: #FFFFFF;\n    color: #000000;\n}"
        if en:
            style += "\n\nQPushButton:checked {\n    background-color: #61136E;\n    color: #FFFFFF;\n}"
        for b in self.direction.buttons():
                b.setStyleSheet(style)
    
    def changeDirection(self, cw):
        """SLOT: changeDirection
                
        Changes the direction of rotation
                
        Expects:
            bool - Whether the direction of rotation is clockwise
                
        Connects to:
            QPushButton.toggled
        
        Emits:
            sendToSerial
        """
        self.clockwise = cw
        if cw:
            dirString = "cw "
        else:
            dirString = "ccw "
        self.sendToSerial.emit("ring rotate " + dirString + str(float((self.rotateDial.value() + 1) / 2)) + ";")
            