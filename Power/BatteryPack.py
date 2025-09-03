#!/usr/bin/python3

# Internal libraries
from Power.BatteryCell import BatteryCell

class BatteryPack:

    # Slices for (self.currentPackVoltage, self.currentPackAmpere, self.currentPackPower) Tuple
    VOLTS = 0
    AMPS = 1
    POWER = 2

    # Number of decimal places to round to when displaying values and asserting values during testing
    SUGGESTED_ROUNDING = 3

    def __init__(self, cell: BatteryCell, packConfiguration: list = ['1S', '1P']):
        """ Initialize a BatteryPack object.
            Assumes a battery pack uses multiple instances of one BatteryCell object, and that all cells have the same state of charge.
            The order of the configuration List does not matter. Both ['3P', '2S'] and ['4S', '10P'] are valid.

        Args:
            cell (BatteryCell): The BatteryCell object used to create a battery pack.
            packConfiguration (list, optional): The series and parellel cell configuration of a battery pack. Defaults to ['1S', '1P'].

        Raises:
            ValueError: If the pack configuration is invalid.
        """
        self.cells = cell
        self.seriesCount = 1
        self.parallelCount = 1
        self.set_series_parallel_pack_configuration(packConfiguration)

        # The real time (current) battery pack voltage, ampere, power, & energy values to be set using property functions
        self.currentPackVoltage = 0
        self.currentPackAmpere  = 0
        self.currentPacktPower  = 0
        self.currentPackEnergy  = 0

        self.minPackVoltage = self.seriesCount * BatteryCell.CHEM_VOLTAGE[cell.chemistry][0]
        self.nominalPackVoltage = self.seriesCount * cell.nominalVoltage
        self.maxPackVoltage = self.seriesCount * BatteryCell.CHEM_VOLTAGE[cell.chemistry][-1]
        self.maxPackAmpere = round(self.parallelCount * (cell.maxAmpere), self.SUGGESTED_ROUNDING)
        self.maxPackPower = self.maxPackVoltage * self.maxPackAmpere


    @property
    def soc(self):
        """Get real time State of Charge (soc) attribute (updates every time BatteryCell object is accessed) for a BatteryPack object

        Returns:
            float: Current State of Charge (soc) of the BatteryPack object in % from 0 to 100.
        """
        return self.cells.stateOfCharge


    @property
    def current_volts_amps_power(self):
        """Get real time voltage, ampere, and power attribute (updates every time BatteryCell object is accessed) for a BatteryPack object

        Returns:
            float: Current voltage of the BatteryPack object in Volts.
            float: Current ampere of the BatteryPack object in Amps.
            float: Current power of the BatteryPack object in Watts.
        """
        self.currentPackVoltage = self.seriesCount * self.cells.currentVoltage
        self.currentPackAmpere = self.parallelCount * self.cells.currentAmpere
        self.currentPackPower = self.currentPackVoltage * self.currentPackAmpere

        return (self.currentPackVoltage, self.currentPackAmpere, self.currentPackPower)


    @property
    def current_pack_energy(self):
        """Get real time energy capacity attribute (updates every time BatteryCell object is accessed) for a BatteryPack object

        Returns:
            float: Current energy capacity of the BatteryPack object in Watts-Hours.
        """
        self.currentPackEnergy = self.seriesCount * self.parallelCount * self.cells.currentEnergy

        return self.currentPackEnergy


    def __str__(self):
        """ Output of print() for a BatteryPack object

        Returns:
            str: String representation of the BatteryPack object.
        """

        return f"BatteryPack([{self.seriesCount}S, {self.parallelCount}P], V={self.current_volts_amps_power[self.VOLTS]}, Max A={self.maxPackAmpere}, Wh Left={round(self.current_pack_energy, self.SUGGESTED_ROUNDING)})"


    def set_series_parallel_pack_configuration(self, configuration: list) -> None:
        """ Set the self.seriesCount and  of the BatteryPack object.

        Args:
            configuration (list): The desired pack configuration.

        Returns:
            ValueError: If the input argument pack configuration is invalid.
        """
        if len(configuration) != 2:
            raise ValueError(f"{configuration} is an invalid pack configuration. The list must contain exactly two elements (e.g. ['6S', '1P'])")

        if configuration[0].endswith('S') or configuration[0].endswith('s'):
            self.seriesCount = int(configuration[0][:-1])
        elif configuration[1].endswith('S') or configuration[1].endswith('s'):
            self.seriesCount = int(configuration[1][:-1])
        else:
            raise ValueError(f"{configuration} is an invalid pack configuration. At least one element of list must end with 'S' or 's'")

        if configuration[0].endswith('P') or configuration[0].endswith('p'):
            self.parallelCount = int(configuration[0][:-1])
        elif configuration[1].endswith('P') or configuration[1].endswith('p'):
            self.parallelCount = int(configuration[1][:-1])
        else:
            raise ValueError(f"{configuration} is an invalid pack configuration. At least one element of list must end with 'P' or 'p'")


if __name__ == "__main__":

    battery = BatteryCell(3.65, 5.0, 10, BatteryCell.AGM)
    batteryPack = BatteryPack(battery, ['1S', '1P'])
    print(batteryPack)
