

class Generation:

    BATTERY_TYPE = 0
    WALL_WART_TYPE = 1


    DEBUG_STATEMENTS_ON = False
    MAX_CHARGED_VOLTAGE = 3.7
    MAX_STATE_OF_CHARGE = 100

    SERIES = 0
    PARALLEL = 1

    def __init__(self, GenerationType):


        if GenerationType.__class__.__name__ == 'Battey':
            self.batteryType = Battery.SERIES
        elif GenerationType == Generation.WALL_WART_TYPE:
            self.batteryType = Battery.PARALLEL
        else:
            raise ValueError("Invalid generation type")


class Battery:


    def __init__(self, packConfiguration: list = ['1S', '1P']):
        self.packConfiguration = packConfiguration                          # Battery pack configuration in series and parallel

        if packConfiguration == ['1S', '1P']:
            self.batteryType = Battery.SERIES
        elif packConfiguration == ['1P', '1S']:
            self.batteryType = Battery.PARALLEL
        else:
            raise ValueError("Invalid battery configuration")


        self.packConfiguration = packConfiguration                          # Battery pack configuration in series and parallel

        if packConfiguration == ['1S', '1P']:
            self.currentVoltage = Generation.MAX_CHARGED_VOLTAGE                # Real time current flow in Volts
            self.currentAmpere = 1.0                                            # Real time current flow in Amps
            self.currentPower = self.currentVoltage * self.currentAmpere        # Units are Watts
            self.energyCapacity = 2.000                                         # Units are Watts-Hours

            self.temperature = 20.0                                             # Units are Celsius
            self.health = 100                                                   # Units are percentage
            self.age = 0                                                        # Units are years
            self.stateOfCharge = Generation.MAX_STATE_OF_CHARGE                 # Units are percentage

            self.rechargeCycleNumber = 0


class BatteryPack:
    def __init__(self, batteryType: int, batteryCount: int):
        self.batteryType = batteryType
        self.batteryCount = batteryCount
