

class Generation:

    DEBUG_STATEMENTS_ON = False
    MAX_CHARGED_VOLTAGE = 3.7

    def __init__(self):
        self.packConfiguration = ('1S', '2P')                               # Battery pack configuration in series and parallel

        self.currentVoltage = Generation.MAX_CHARGED_VOLTAGE                # Real time current flow in Volts
        self.currentAmpere = 1.0                                            # Real time current flow in Amps
        self.currentPower = self.currentVoltage * self.currentAmpere        # Units are Watts
        self.energyCapacity = 2.000                                             # Units are Watts-Hours

        self.temperature = 20.0                                             # Units are Celsius
        self.health = 100                                                   # Units are percentage
        self.age = 0

        self.rechargeCycleNumber = 0
