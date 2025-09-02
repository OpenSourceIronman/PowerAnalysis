#!/usr/bin/python3

# Internal libraries
from Power.BatteryCell import BatteryCell

class BatteryPack:

    VOLTS = 0
    AMPS = 1
    POWER = 2
    SUGGESTED_ROUNDING = 3
    WILL_BE_SET_USING_PROPERTY_FUNCTIONS = -1

    def __init__(self, battery: BatteryCell, packConfiguration: list = ['1S', '1P']):
        """ Initialize a BatteryPack object.
            Assumes pack uses multiple instances of one BatteryCell object, and that all cells have the same state of charge
            The order of the configuration List does not matter. Both ['3P', '2S'] and ['4S', '10P'] are valid.

        Args:
            battery (BatteryCell): The BatteryCell object used in the pack.
            packConfiguration (list, optional): The configuration of the pack. Defaults to ['1S', '1P'].

        Raises:
            ValueError: If the pack configuration is invalid.
        """
        self.cells = battery
        self.seriesCount = 1
        self.parallelCount = 1
        self.packConfiguration = packConfiguration
        self.set_series_parallel_pack_configuration(packConfiguration)


        self.currentPackVoltage = self.WILL_BE_SET_USING_PROPERTY_FUNCTIONS
        self.currentPackAmpere = self.WILL_BE_SET_USING_PROPERTY_FUNCTIONS
        self.currentPacktPower = self.WILL_BE_SET_USING_PROPERTY_FUNCTIONS
        self.currentPackEnergy = self.WILL_BE_SET_USING_PROPERTY_FUNCTIONS

        self.minPackVoltage = self.seriesCount * BatteryCell.CHEM_VOLTAGE[battery.chemistry][0]
        self.nominalPackVoltage = self.seriesCount * battery.nominalVoltage
        self.maxPackVoltage = self.seriesCount * BatteryCell.CHEM_VOLTAGE[battery.chemistry][-1]
        self.maxPackAmpere = round(self.parallelCount * (battery.maxAmpere), self.SUGGESTED_ROUNDING)
        self.maxPackPower = self.maxPackVoltage * self.maxPackAmpere


    @property
    def soc(self):
        return self.cells.stateOfCharge


    @property
    def current_volts_amps_power(self):
        self.currentPackVoltage = self.seriesCount * self.cells.currentVoltage
        self.currentPackAmpere = self.parallelCount * self.cells.currentAmpere
        self.currentPacktPower = self.currentPackVoltage * self.currentPackAmpere

        return self.currentPackVoltage, self.currentPackAmpere, self.currentPacktPower


    @property
    def current_pack_energy(self):
        self.currentPackEnergy = self.seriesCount * self.parallelCount * self.cells.currentEnergy  # Units are Watts-Hours
        return self.currentPackEnergy


    def __str__(self):
        """ Output of print() for BatteryPack objects

        Returns:
            str: String representation of the BatteryPack object.
        """

        return f"BatteryPack({self.packConfiguration}, V={self.current_volts_amps_power[self.VOLTS]}, Max A={self.maxPackAmpere}, Wh Left={round(self.current_pack_energy, self.SUGGESTED_ROUNDING)})"


    def set_series_parallel_pack_configuration(self, configuration: list) -> None:
        """ Set the self.seriesCount and  of the BatteryPack object.

        Args:
            configuration (list): The pack configuration list.
        """
        if len(configuration) != 2:
            raise ValueError(f"{configuration} is an invalid pack configuration. The list must contain exactly two elements (e.g. ['6S', '1P'])")

        if configuration[0].endswith('S') or configuration[0].endswith('s'):
            self.seriesCount = int(configuration[0][:-1])
        elif configuration[1].endswith('S') or configuration[1].endswith('s'):
            self.seriesCount = int(configuration[1][:-1])
        else:
            raise ValueError(f"{configuration} is an invalid pack configuration. At least one element must end with 'S' or 's'")

        if configuration[0].endswith('P') or configuration[0].endswith('p'):
            self.parallelCount = int(configuration[0][:-1])
        elif configuration[1].endswith('P') or configuration[1].endswith('p'):
            self.parallelCount = int(configuration[1][:-1])
        else:
            raise ValueError(f"{configuration} is an invalid pack configuration. At least one element must end with 'P' or 'p'")


if __name__ == "__main__":

    battery = BatteryCell(3.65, 5.0, 10, BatteryCell.AGM)
    batteryPack = BatteryPack(battery, ['1S', '1P'])
    print(batteryPack)
