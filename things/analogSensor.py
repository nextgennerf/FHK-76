from things.ioModule import IOModule

class AnalogSensor(IOModule):
    """CLASS: AnalogSensor
    
    This IO Module represents an analog sensor. It is currently under construction.
    """
    #TODO: finish building

    def __init__(self, initVal, supply, sim):
        super().__init__(sim)
        self.vcc = supply
        self.value = initVal