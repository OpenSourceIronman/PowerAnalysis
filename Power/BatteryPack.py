from Power.BatteryCell import BatteryCell

class BatteryPack:

    SERIES = 0
    PARALLEL = 1

    def __init__(self, battery: BatteryCell, packConfiguration: list = ['2S', '1P']):
        self.cell = battery
        self.packConfiguration = packConfiguration
        self.seriesCount = self.parse_pack_configuration(packConfiguration[self.SERIES])
        self.parallelCount = self.parse_pack_configuration(packConfiguration[self.PARALLEL])
        self.soc = battery.stateOfCharge

        self.currentPackVoltage = self.seriesCount * battery.currentVoltage
        self.currentPackAmpere = self.parallelCount * battery.currentAmpere
        self.currentPower = self.currentPackVoltage * self.currentPackAmpere  # Units are Watts
        self.packEnergyCapacity = self.seriesCount * self.parallelCount * battery.currentEnergy                    # Units are Watts-Hours

        self.minPackVoltage = self.seriesCount * BatteryCell.CHEM_VOLTAGE[battery.chemistry][0]
        self.nominalPackVoltage = self.seriesCount * battery.nominalVoltage
        self.maxPackVoltage = self.seriesCount * BatteryCell.CHEM_VOLTAGE[battery.chemistry][-1]
        self.maxPackAmpere= round(self.parallelCount * (battery.maxAmpere), 1)
        self.maxPackPower = self.maxPackVoltage * self.maxPackAmpere

    def __str__(self):
        """ Output of print() for BatteryPack objects

        Returns:
            str: String representation of the BatteryPack object.
        """

        return f"BatteryPack({self.packConfiguration}, V={self.currentPackVoltage}, Max A={self.maxPackAmpere}, Total Wh={self.packEnergyCapacity})"

    def parse_pack_configuration(self, input: str) -> int:
        count = int(input[:-1]) # String without its last character.

        return count
