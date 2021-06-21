import json
from enum import IntEnum
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QRegularExpression
from PyQt5.QtWidgets import QDial, QCheckBox, QLabel, QPushButton, QRadioButton, QStackedWidget
from PyQt5.Qt import QPixmap

class Animation(IntEnum):
    """ENUM: Animation
    
    Integers representing different animation modes
    """
    STATIC = 0
    BREATHE = 1
    CYCLE = 2
    SOLID_SPIN = 3
    FADE_SPIN = 4
    RAINBOW_SPIN = 5

class Color(IntEnum):
    """ENUM: Color
    
    Integers representing different color schemes for the pixel ring
    """
    SINGLE = 0
    RAINBOW = 1
    RGB = 2
    YCM = 3
    RYGCBM = 4

#FUTURE: Create superclass for all NeoPixel tool classes
#FUTURE: Recreate layout images to allow for the on pixels to reflect actual color
class RingTool(QObject):
    """CLASS: RingTool
    
    This class handles some of the interactions between the objects in a pair of QToolBox panes for a ring of 24 NeoPixels and sends messages to the Metro Mini when settings change.
    
    SIGNALS                                SLOTS
    ----------------------    ------------------
    clearAlternate      ()    ()    colorChanged
    enableAlternate (bool)    (*)  layoutChanged
    sendToSerial     (str)    (*) patternChanged
    setEightCount       ()    ()    sendNewValue
                              (int) updateSquare
    """
    
    clearAlternate = pyqtSignal()
    """SIGNAL: clearAlternate
            
    Clears the alternate layout check box
            
    Broadcasts:
        none
            
    Connects to:
        QCheckBox.setChecked
    """
    
    enableAlternate = pyqtSignal(bool)
    """SIGNAL: enableAlternate
            
    Connects to the alternate layout checkbox's setEnabled slot
            
    Broadcasts:
        bool - Whether the check box should be enabled
            
    Connects to:
        QCheckBox.setEnabled
    """
    
    sendToSerial = pyqtSignal(str)
    """SIGNAL: sendToSerial
            
    Delivers a message to be sent over serial
    
    Broadcasts:
        str - The message being sent
            
    Connects to:
        MetroMini.broadcast
    """
    
    setEightCount = pyqtSignal()
    """SIGNAL: setEightCount
            
    Virtually clicks the '8' count button
            
    Broadcasts:
        none
            
    Connects to:
        QRadioButton.click (MainWindow.button8)
    """
    
    #TODO: Add argument for passing initial settings
    def __init__(self, patternWidget, colorWidget, serial):
        super().__init__()
        
        self.locationOffset = 0 # Since I cannot control which LED is where, this will allow me to shift the dial values to real locations.
        
        with open("styles.json") as file:
            self.styles = json.load(file)
            file.close()
        
        self.timeDial = patternWidget.findChild(QDial)
        self.timeDial.sliderReleased.connect(self.sendNewValue)
        
        self.aLabels = []
        for l in patternWidget.findChildren(QLabel):
            n = l.objectName()
            if n == "ANIMATION" or n == "timeLabel":
                self.aLabels.append(l)
                if n == "timeLabel":
                    self.timeLabel = l
                    self.timeDial.valueChanged.connect(lambda val: self.timeLabel.setText(f"{val} sec"))
            elif n == "layoutImage":
                self.layout = l
        
        self.directions = patternWidget.findChildren(QPushButton)[0].group()
        for b in self.directions.buttons():
            if b.objectName().endswith("CLW"):
                self.directions.setId(b, 0)
            elif b.objectName().endswith("CCW"):
                self.directions.setId(b, 1)
        self.directions.button(0).toggled.connect(self.patternChanged)
        
        self.patterns = None
        self.patternDict = {}
        self.counts = None
        for b in patternWidget.findChildren(QRadioButton):
            if b.objectName().startswith("front"):
                if self.patterns is None:
                    self.patterns = b.group()
                if b.objectName()[5:].startswith("Static"):
                    self.patterns.setId(b, Animation.STATIC)
                    self.patternDict[self.patterns.id(b)] = "static"
                if b.objectName()[5:].startswith("Breathe"):
                    self.patterns.setId(b, Animation.BREATHE)
                    self.patternDict[self.patterns.id(b)] = "breathe"
                if b.objectName()[5:].startswith("Solid"):
                    self.patterns.setId(b, Animation.SOLID_SPIN)
                    self.patternDict[self.patterns.id(b)] = "spin"
                if b.objectName()[5:].startswith("Fade"):
                    self.patterns.setId(b, Animation.FADE_SPIN)
                    self.patternDict[self.patterns.id(b)] = "fade"
                if b.objectName()[5:].startswith("Rainbow"):
                    self.patterns.setId(b, Animation.RAINBOW_SPIN)
                    self.patternDict[self.patterns.id(b)] = "rainbow"
            if b.objectName().startswith("button"):
                if self.counts is None:
                    self.counts = b.group()
                self.counts.setId(b, int(b.text()))
        self.patterns.idClicked.connect(self.patternChanged)
        self.counts.idClicked.connect(self.layoutChanged)
        self.setEightCount.connect(self.counts.button(8).click)
        
        self.alternateLayout = patternWidget.findChild(QCheckBox)
        self.alternateLayout.toggled.connect(self.layoutChanged)
        self.clearAlternate.connect(lambda: self.alternateLayout.setChecked(False))
        self.enableAlternate.connect(self.alternateLayout.setEnabled)
        
        self.colors = colorWidget.findChildren(QRadioButton)[0].group()
        self.colorDict = {}
        self.otherColors = []
        for b in self.colors.buttons():
            if b.objectName().startswith("single"):
                self.colors.setId(b, Color.SINGLE)
                b.toggled.connect(lambda x: colorWidget.findChild(QStackedWidget).setCurrentIndex(int(x))) # It's a cheat, but hey, it works!
            elif b.objectName().startswith("rainbow"):
                self.colors.setId(b, Color.RAINBOW)
                self.patterns.button(Animation.RAINBOW_SPIN).clicked.connect(b.setChecked)
            elif b.objectName().startswith("rgb"):
                self.colors.setId(b, Color.RGB)
            elif b.objectName().startswith("ycm"):
                self.colors.setId(b, Color.YCM)
            elif b.objectName().startswith("rygcbm"):
                self.colors.setId(b, Color.RYGCBM)
            self.colorDict[self.colors.id(b)] = b.objectName().removesuffix("Button")
            if not b.objectName().startswith("rainbow"):
                self.otherColors.append(b) # This helps with disabling color buttons in patternChanged
            
        self.colors.idClicked.connect(self.colorChanged)
        
        for d in colorWidget.findChildren(QDial):
            if d.objectName().startswith("hue"):
                self.hueDial = d
            else:
                self.stepDial = d
        self.hueDial.valueChanged.connect(self.updateSquare)
        self.hueDial.sliderReleased.connect(self.sendNewValue)
        self.stepDial.sliderReleased.connect(self.sendNewValue)
        
        for l in colorWidget.findChildren(QLabel):
            if not l.objectName().isupper():
                if l.objectName().startswith("hue"):
                    self.hueLabel = l
                else:
                    self.stepLabel = l
        self.stepDial.valueChanged.connect(lambda val: self.stepLabel.setText(f"{max(float(val / 2.0), 0.5)} sec"))
        self.sLabels = colorWidget.findChildren(QLabel, QRegularExpression("^step", QRegularExpression.CaseInsensitiveOption))
        
        self.sendToSerial.connect(serial.broadcast)
    
    def initialize(self):
        """METHOD: initialize
                
        Sends initial settings to the Metro Mini (calls patternChanged as a method)
                
        Called by:
            MainWindow.initializeSerialObjects
                
        Arguments:
            none
                
        Returns:
            none
        """
        self.layout.setPixmap(QPixmap(f"layouts/{self.counts.checkedId()}{'a' if self.alternateLayout.isChecked() else ''}.png").scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, \
                                                                                                                                        Qt.TransformationMode.SmoothTransformation))
        self.patternChanged(self.patterns.checkedId())
    
    def patternChanged(self, arg):
        """SLOT: patternChanged
                
        Updates the GUI when the pattern is changed and initiates the transmission of an instruction to the Metro Mini
                
        Expects:
            int - The enum value of the new animation pattern
            bool - The new rotation direction for appropriate patterns
                
        Connects to:
            QButtonGroup.idClicked (patterns, broadcasts int)
            QPushButton.toggled (MainWindow.spinCLW, broadcasts bool)
        """
        if type(arg) is int: # Only calls from radio buttons require GUI changes
            self.changeStyle(arg != Animation.STATIC, *self.aLabels)
            noMotion = arg == Animation.STATIC or arg == Animation.BREATHE
            self.changeStyle(not noMotion, *self.directions.buttons())
            for cb in self.counts.buttons():
                num = self.counts.id(cb)
                if num == 1:
                    self.changeStyle(arg != Animation.STATIC and arg != Animation.RAINBOW_SPIN, cb)
                elif num == 12:
                    self.changeStyle(noMotion, cb)
                elif num == 24:
                    self.changeStyle(noMotion or arg == Animation.RAINBOW_SPIN, cb)
                else:
                    self.changeStyle(arg != Animation.RAINBOW_SPIN, cb)
            if (arg == Animation.FADE_SPIN or arg == Animation.SOLID_SPIN) and self.counts.checkedId() > 8: # This ensures a valid count button is always checked
                self.setEightCount.emit()
            self.changeStyle(arg != Animation.RAINBOW_SPIN, *self.otherColors, *self.sLabels)
        self.updateCheckBox()
        self.composeAndSend()
    
    def layoutChanged(self):
        """SLOT: layoutChanged
                
        Updates the GUI when the layout is changed and initiates the transmission of an instruction to the Metro Mini
                
        Expects:
            none
                
        Connects to:
            QButtonGroup.idClicked (counts)
            QCheckBox.clicked
        """
        self.layout.setPixmap(QPixmap(f"layouts/{self.counts.checkedId()}{'a' if self.alternateLayout.isChecked() else ''}.png").scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, \
                                                                                                                                        Qt.TransformationMode.SmoothTransformation))
        self.updateCheckBox()
        self.composeAndSend()
        
    def updateCheckBox(self):
        """METHOD: updateCheckBox
                
        Check whether the alternate layout check box needs to change appearance or enabled state
                
        Called by:
            patternChanged, layoutChanged
                
        Arguments:
            none
        
        Emits:
            enableAlternate, clearAlternate
        """
        pattern, count = self.patterns.checkedId(), self.counts.checkedId()
        alternateEnabled = (pattern == Animation.STATIC or pattern == Animation.BREATHE) and not (count == 1 or count == 8 or count == 24)
        self.changeStyle(alternateEnabled, self.alternateLayout)
        self.enableAlternate.emit(alternateEnabled)
        if not alternateEnabled:
            self.clearAlternate.emit()
        
    def colorChanged(self):
        """SLOT: colorChanged
                
        Calls composeAndSend to avoid using it as a slot
                
        Expects:
            none
                
        Connects to:
            QButtonGroup.idClicked (colors)
        """
        self.composeAndSend()
        
    def composeAndSend(self):
        """METHOD: composeAndSend
                
        Compiles a new instruction message and sends it to the Metro Mini
                
        Called by:
            patternChanged, layoutChanged, colorChanged
                
        Arguments:
            none
                
        Returns:
            none
        
        Emits:
            sendToSerial
        """
        pattern = self.patterns.checkedId()
        msg = f"ring {self.patternDict[pattern]} {self.counts.checkedId()}{'a' if self.alternateLayout.isChecked() else ''}"
        
        if pattern != Animation.STATIC:
            msg += f" {self.timeDial.value()}"
            if pattern != Animation.BREATHE:
                msg += f" {'clw' if self.directions.button(0).isChecked() else 'ccw'}"
            
        if pattern == Animation.RAINBOW_SPIN:
            self.sendToSerial.emit(msg + ";")
        else:
            self.sendToSerial.emit(msg + f" {self.colorDict[self.colors.checkedId()]} {self.hueDial.value() * 2048 if self.colors.checkedId() == Color.SINGLE else float(self.stepDial.value() / 2.0)};")
                
    def sendNewValue(self):
        """SLOT: sendNewValue
    
        Checks a new dial value to make sure it's valid and sends it to the Metro Mini
    
        Expects:
            none
    
        Connects to:
            QDial.sliderReleased
    
        Emits:
            sendToSerial
        """
        source = self.sender()
        newVal = source.value()
        if source is self.hueDial:
            newVal = newVal * 2048
        elif source is self.stepDial:
            if newVal == 0:
                source.setValue(1)
            newVal = float(newVal / 2.0)
        self.sendToSerial.emit(f'ring change {source.objectName().removesuffix("Dial")} {newVal};')
    
    def updateSquare(self, hue):
        """SLOT: updateSquare
                
        Updates the color of the square indicating the current color
        
        Expects:
            int - The hue value of the new color in degrees
        
        Connects to:
            QDial.valueChanged
        """
        self.hueLabel.setStyleSheet("border: 2px solid #000000;\n"
                                    f"background-color: hsv({hue * 11.25}, 255, 255)")
        
    def changeStyle (self, en, *widgets):
        """METHOD: changeStyle
                
        Changes the appearance of a given widget using the style JSON
                
        Called by:
            patternChanged
                
        Arguments:
            bool - Whether the widget should appear enabled or disabled
            QWidget - One or more widgets that need to be updated
                
        Returns:
            none
        """
        for w in widgets:
            if type(w).__name__ == "QRadioButton" and w.group() is self.counts: # This needs to be handled separately because they're not standard radio buttons
                w.setStyleSheet(self.styles["LayoutCountButton-" + str(en)])
            else:
                w.setStyleSheet(self.styles[type(w).__name__ + "-" + str(en)])