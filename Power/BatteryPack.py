from Power.BatteryCell import BatteryCell

class BatteryPack:

    SERIES = 0
    PARALLEL = 1

    def __init__(self, packConfiguration: list = ['2S', '1P'], battery: BatteryCell = None):
        self.packConfiguration = packConfiguration
        self.seriesCount = self.parse_pack_configuration(packConfiguration[self.SERIES])
        self.parallelCount = self.parse_pack_configuration(packConfiguration[self.PARALLEL])

        self.currentPackVoltage = self.seriesCount * battery.currentVoltage
        self.currentPackAmpere = self.parallelCount * battery.currentAmpere
        self.currentPower = self.currentPackVoltage * self.currentPackAmpere  # Units are Watts
        self.energyCapacity = energy                    # Units are Watts-Hours

        self.minPackVoltage = self.seriesCount * BatteryCell.CHEM_VOLTAGE[battery.chemistry][0]
        idx = (np.abs(BatteryCell.CHEM_SOC[battery.chemistry]- 50)).argmin() # 50% of CHEM_SOC arrays
        self.nominalPackVoltage = self.seriesCount * BatteryCell.CHEM_VOLTAGE[battery.chemistry][idx]
        self.maxPackVoltage = self.seriesCount * BatteryCell.CHEM_VOLTAGE[battery.chemistry][-1]
        self.maxPackAmpere= battery.cRating *  battery.energy / battery.nominalPackVoltage
        self.maxPackPower = self.nominalPackVoltage * self.maxPackAmpere

    def parse_pack_configuration(self, input: str) -> int:
        count = int(input[:-1]) # String without its last character.

        return count
