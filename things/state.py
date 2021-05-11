from enum import Enum

class State(Enum):
    """ENUM: State
    
    Emojis used to display the state of various indicators. This is in its own file primarily because inserting the emojis changes the line spacing.
    """
    ON = "🟢"
    OFF = "🔴"