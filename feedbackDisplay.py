from enum import Enum
from PyQt5.QtCore import QObject, QStateMachine, QState, QTimer, pyqtSignal, QEvent

DELAY_BEFORE_SET = 1000 # Represents the time delay in milliseconds between the last GUI button press and the display returning to normal
REFRESH_PERIOD = 500 # Represents the amount of time in milliseconds between sending data requests to the Metro Mini

class Color(Enum):
    """ENUM: Color
    
    Hex strings representing different display colors since that's all that changes in the style sheet
    """
    BLACK = "000000"
    GREEN = "00FF00"
    RED = "FF0000"

class DisplayState(QState):
    """CLASS: DisplayState
    
    This subclass of QState has additional functions to control the LCD display.
    
    SIGNALS                             SLOTS
    ----------------    ---------------------
    done          ()    (float) updateDisplay
    newValue (float)
    """
    
    newValue = pyqtSignal(float)
    """SIGNAL: newValue
    
    Internal signal used to update the value displayed on the LCD
    
    Broadcasts:
        float - The new number to be displayed
    
    Connects to:
        QLCDNumber.display
    """
    
    done = pyqtSignal()
    """SIGNAL: done
    
    Internal signal used to trigger the transition to the waiting state
    
    Broadcasts:
        none
    
    Connects to:
        (FeedbackDisplay.upState, FeedbackDisplay.downState) FeedbackDisplay.stateMachine transition (* -> FeedbackDisplay.waitState)
    """
    
    def __init__(self, lcd, color, name, value = None):
        super().__init__()
        ###DEBUG ONLY###
        self.name = name
        # self.eventLookup(-1)
        ###END DEBUG###
        self.color = color
        self.lcd = lcd
        self.newValue.connect(lcd.display)
        self.value = value # The existence (i.e. not None) of this value is how you know the state cares about the actual value instead of the target value
    
    def onEntry(self, event):
        """METHOD: onEntry
                
        Superclass method override, automatically called when the state is entered
                
        Arguments:
            none
                
        Returns:
            none
        
        Emits:
            newValue, done
        """
        ###DEBUG ONLY###
        if self.name is not None:
            print(self.name)
        # print(self.eventLookup(event.type()))
        ###END DEBUG###
        self.lcd.setStyleSheet("border: 3px solid #61136e;\n"
                               "border-radius: 8px;\n"
                               f"color: #{self.color.value}")
        dispVal = self.machine().getTarget() if self.value is None else self.value
        self.newValue.emit(dispVal)
        self.done.emit()
    
    def updateDisplay(self, newVal):
        """SLOT: updateDisplay
                
        Used to update the displayed and stored values at a time other than right when the state is entered
                
        Expects:
            float - The new value to display/store
                
        Connects to:
            (FeedbackState.defaultState) MetroMini.newDataAvailable [Connected by MainWindow]
        
        Emits:
            newValue
        """
        self.value = float(newVal)
        self.newValue.emit(self.value)
        
    ###DEBUG ONLY###
    # def eventLookup (self, num):
    #     if num == -1:
    #         self.eventTypes = {"0": "QEvent::None",
    #                           "114": "QEvent::ActionAdded",
    #                           "113": "QEvent::ActionChanged",
    #                           "115": "QEvent::ActionRemoved",
    #                           "99": "QEvent::ActivationChange",
    #                           "121": "QEvent::ApplicationActivate",
    #                           "122": "QEvent::ApplicationDeactivate",
    #                           "36": "QEvent::ApplicationFontChange",
    #                           "37": "QEvent::ApplicationLayoutDirectionChange",
    #                           "38": "QEvent::ApplicationPaletteChange",
    #                           "214": "QEvent::ApplicationStateChange",
    #                           "35": "QEvent::ApplicationWindowIconChange",
    #                           "68": "QEvent::ChildAdded",
    #                           "69": "QEvent::ChildPolished",
    #                           "71": "QEvent::ChildRemoved",
    #                           "40": "QEvent::Clipboard",
    #                           "19": "QEvent::Close",
    #                           "200": "QEvent::CloseSoftwareInputPanel",
    #                           "178": "QEvent::ContentsRectChange",
    #                           "82": "QEvent::ContextMenu",
    #                           "183": "QEvent::CursorChange",
    #                           "52": "QEvent::DeferredDelete",
    #                           "60": "QEvent::DragEnter",
    #                           "62": "QEvent::DragLeave",
    #                           "61": "QEvent::DragMove",
    #                           "63": "QEvent::Drop",
    #                           "170": "QEvent::DynamicPropertyChange",
    #                           "98": "QEvent::EnabledChange",
    #                           "10": "QEvent::Enter",
    #                           "150": "QEvent::EnterEditFocus",
    #                           "124": "QEvent::EnterWhatsThisMode",
    #                           "206": "QEvent::Expose",
    #                           "116": "QEvent::FileOpen",
    #                           "8": "QEvent::FocusIn",
    #                           "9": "QEvent::FocusOut",
    #                           "23": "QEvent::FocusAboutToChange",
    #                           "97": "QEvent::FontChange",
    #                           "198": "QEvent::Gesture",
    #                           "202": "QEvent::GestureOverride",
    #                           "188": "QEvent::GrabKeyboard",
    #                           "186": "QEvent::GrabMouse",
    #                           "159": "QEvent::GraphicsSceneContextMenu",
    #                           "164": "QEvent::GraphicsSceneDragEnter",
    #                           "166": "QEvent::GraphicsSceneDragLeave",
    #                           "165": "QEvent::GraphicsSceneDragMove",
    #                           "167": "QEvent::GraphicsSceneDrop",
    #                           "163": "QEvent::GraphicsSceneHelp",
    #                           "160": "QEvent::GraphicsSceneHoverEnter",
    #                           "162": "QEvent::GraphicsSceneHoverLeave",
    #                           "161": "QEvent::GraphicsSceneHoverMove",
    #                           "158": "QEvent::GraphicsSceneMouseDoubleClick",
    #                           "155": "QEvent::GraphicsSceneMouseMove",
    #                           "156": "QEvent::GraphicsSceneMousePress",
    #                           "157": "QEvent::GraphicsSceneMouseRelease",
    #                           "182": "QEvent::GraphicsSceneMove",
    #                           "181": "QEvent::GraphicsSceneResize",
    #                           "168": "QEvent::GraphicsSceneWheel",
    #                           "18": "QEvent::Hide",
    #                           "27": "QEvent::HideToParent",
    #                           "127": "QEvent::HoverEnter",
    #                           "128": "QEvent::HoverLeave",
    #                           "129": "QEvent::HoverMove",
    #                           "96": "QEvent::IconDrag",
    #                           "101": "QEvent::IconTextChange",
    #                           "83": "QEvent::InputMethod",
    #                           "207": "QEvent::InputMethodQuery",
    #                           "169": "QEvent::KeyboardLayoutChange",
    #                           "6": "QEvent::KeyPress",
    #                           "7": "QEvent::KeyRelease",
    #                           "89": "QEvent::LanguageChange",
    #                           "90": "QEvent::LayoutDirectionChange",
    #                           "76": "QEvent::LayoutRequest",
    #                           "11": "QEvent::Leave",
    #                           "151": "QEvent::LeaveEditFocus",
    #                           "125": "QEvent::LeaveWhatsThisMode",
    #                           "88": "QEvent::LocaleChange",
    #                           "176": "QEvent::NonClientAreaMouseButtonDblClick",
    #                           "174": "QEvent::NonClientAreaMouseButtonPress",
    #                           "175": "QEvent::NonClientAreaMouseButtonRelease",
    #                           "173": "QEvent::NonClientAreaMouseMove",
    #                           "177": "QEvent::MacSizeChange",
    #                           "43": "QEvent::MetaCall",
    #                           "102": "QEvent::ModifiedChange",
    #                           "4": "QEvent::MouseButtonDblClick",
    #                           "2": "QEvent::MouseButtonPress",
    #                           "3": "QEvent::MouseButtonRelease",
    #                           "5": "QEvent::MouseMove",
    #                           "109": "QEvent::MouseTrackingChange",
    #                           "13": "QEvent::Move",
    #                           "197": "QEvent::NativeGesture",
    #                           "208": "QEvent::OrientationChange",
    #                           "12": "QEvent::Paint",
    #                           "39": "QEvent::PaletteChange",
    #                           "131": "QEvent::ParentAboutToChange",
    #                           "21": "QEvent::ParentChange",
    #                           "212": "QEvent::PlatformPanel",
    #                           "217": "QEvent::PlatformSurface",
    #                           "75": "QEvent::Polish",
    #                           "74": "QEvent::PolishRequest",
    #                           "123": "QEvent::QueryWhatsThis",
    #                           "106": "QEvent::ReadOnlyChange",
    #                           "199": "QEvent::RequestSoftwareInputPanel",
    #                           "14": "QEvent::Resize",
    #                           "204": "QEvent::ScrollPrepare",
    #                           "205": "QEvent::Scroll",
    #                           "117": "QEvent::Shortcut",
    #                           "51": "QEvent::ShortcutOverride",
    #                           "17": "QEvent::Show",
    #                           "26": "QEvent::ShowToParent",
    #                           "50": "QEvent::SockAct",
    #                           "192": "QEvent::StateMachineSignal",
    #                           "193": "QEvent::StateMachineWrapped",
    #                           "112": "QEvent::StatusTip",
    #                           "100": "QEvent::StyleChange",
    #                           "87": "QEvent::TabletMove",
    #                           "92": "QEvent::TabletPress",
    #                           "93": "QEvent::TabletRelease",
    #                           "171": "QEvent::TabletEnterProximity",
    #                           "172": "QEvent::TabletLeaveProximity",
    #                           "219": "QEvent::TabletTrackingChange",
    #                           "22": "QEvent::ThreadChange",
    #                           "1": "QEvent::Timer",
    #                           "120": "QEvent::ToolBarChange",
    #                           "110": "QEvent::ToolTip",
    #                           "184": "QEvent::ToolTipChange",
    #                           "194": "QEvent::TouchBegin",
    #                           "209": "QEvent::TouchCancel",
    #                           "196": "QEvent::TouchEnd",
    #                           "195": "QEvent::TouchUpdate",
    #                           "189": "QEvent::UngrabKeyboard",
    #                           "187": "QEvent::UngrabMouse",
    #                           "78": "QEvent::UpdateLater",
    #                           "77": "QEvent::UpdateRequest",
    #                           "111": "QEvent::WhatsThis",
    #                           "118": "QEvent::WhatsThisClicked",
    #                           "31": "QEvent::Wheel",
    #                           "132": "QEvent::WinEventAct",
    #                           "24": "QEvent::WindowActivate",
    #                           "103": "QEvent::WindowBlocked",
    #                           "25": "QEvent::WindowDeactivate",
    #                           "34": "QEvent::WindowIconChange",
    #                           "105": "QEvent::WindowStateChange",
    #                           "33": "QEvent::WindowTitleChange",
    #                           "104": "QEvent::WindowUnblocked",
    #                           "203": "QEvent::WinIdChange",
    #                           "126": "QEvent::ZOrderChange", }
    #     else:
    #         return self.eventTypes[str(num)]
    ###END DEBUG###

class FeedbackDisplay(QObject):
    """CLASS: FeedbackDisplay
    
    This class wraps a QStateMachine and a QLCDNumber in the GUI so it can keep track of a target value and prevent competing display changes.
    
    SIGNALS                                 SLOTS
    ---------------------    --------------------
    targetChanged (float)    (float) changeTarget
    """
    
    targetChanged = pyqtSignal(float)
    """SIGNAL: targetChanged
    
    Emitted when the target value has changed
    
    Broadcasts:
        float - The new target value
    
    Connects to:
        TODO: (probably necessary for FPS)
    """
    
    raiseTarget = pyqtSignal()
    """SIGNAL: raiseTarget
            
    Internal state change signal
            
    Broadcasts:
        none
            
    Connects to:
        stateMachine transition (* -> upState)
    """
    
    lowerTarget = pyqtSignal()
    """SIGNAL: lowerTarget
            
    Internal state change signal
            
    Broadcasts:
        none
            
    Connects to:
        stateMachine transition (* -> downState)
    """

    def __init__(self, lcd, targetVal, serial = None, template = None):
        super().__init__()
        
        self.stateMachine = QStateMachine()
        
        ###DEBUG ONLY###
        names = [None, None, None] if serial is None else ["default", "up", "down"]
        ###END DEBUG###
        
        self.defaultState = DisplayState(lcd, Color.BLACK, names[0], 0.0) # TODO: Remove name argument after debug
        self.upState = DisplayState(lcd, Color.GREEN, names[1]) # TODO: Remove name argument after debug
        self.downState = DisplayState(lcd, Color.RED, names[2]) # TODO: Remove name argument after debug
        self.waitState = QState()
        
        self.setTimer = QTimer()
        self.setTimer.setInterval(DELAY_BEFORE_SET)
        self.setTimer.setSingleShot(True)
        self.waitState.entered.connect(self.setTimer.start)
        self.waitState.exited.connect(self.setTimer.stop)
        
        for s in [self.defaultState, self.upState, self.downState, self.waitState]:
            self.stateMachine.addState(s)
            s.addTransition(self.raiseTarget, self.upState)
            s.addTransition(self.lowerTarget, self.downState)
        for s in [self.upState, self.downState]:
            s.addTransition(s.done, self.waitState)
        self.waitState.addTransition(self.setTimer.timeout, self.defaultState)
        
        self.stateMachine.setInitialState(self.defaultState)
        
        self.target = float(targetVal)
        
        if serial is not None:
            self.serial = serial
            self.template = template
            
            self.serial.newDataAvailable.connect(self.defaultState.updateDisplay)
            
            self.waitState.exited.connect(lambda x = self.template.format(self.target): self.serial.writeData(x))
            
            self.requestTimer = QTimer()
            self.requestTimer.setInterval(REFRESH_PERIOD)
            self.requestTimer.timeout.connect(lambda x = "request;": self.serial.writeData(x))
            self.defaultState.entered.connect(self.requestTimer.start)
            self.defaultState.exited.connect(self.requestTimer.stop)

        self.stateMachine.start()
    
    def getTarget(self):
        """METHOD: getTarget
    
        Access method for the current target value
    
        Called by:
            DisplayState.onEntry
    
        Arguments:
            none
    
        Returns:
            float - The current target value
        """
        return self.target
        
    def changeTarget(self, delta):
        """SLOT: changeTarget
    
        Applies a numeric change to the stored target value and directs the QLCDNumber to show that change.
    
        Expects:
            float: The amount by which to shift the target value
    
        Connects to:
            QPushButton.clicked (MainWindow.fpsUpButton, MainWindow.fpsDownButton, MainWindow.psiUpButton, MainWindow.psiDownButton)
            
        Emits:
            raiseTarget, lowerTarget, targetChanged
        """
        self.target += float(delta)
        if delta > 0:
            self.raiseTarget.emit()
        elif delta < 0:
            self.lowerTarget.emit()
        self.targetChanged.emit(self.target)