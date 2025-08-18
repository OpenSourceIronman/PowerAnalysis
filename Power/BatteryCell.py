#!/.venvPowerAnalysis/bin/python3

import numpy as np
import math

class BatteryCell:

    MAX_STATE_OF_CHARGE = 100       # Units are in perentage

    # Three valid battery cell chemistry types
    LI_FE_P_O4 = 'LI_FE_P_O4'
    LI_CO_O2 = 'LI_CO_O2'
    LI_M_N2_04 = 'LI_M_N2_04'
    # LEAD_ACID =
    # AIR_MAT =
    # LI_ION =

    # Cell voltages for different chemistries at predefined soc steps (CHEM_SOC)
    CHEM_VOLTAGE = {
        'LI_FE_P_O4': np.array([2.80, 2.90, 3.00, 3.08, 3.12, 3.16, 3.20, 3.24, 3.28, 3.30, 3.32, 3.34, 3.36, 3.38, 3.40, 3.42, 3.44, 3.48, 3.50, 3.55, 3.60, 3.65]),
        'LI_CO_O2':   np.array([3.00, 3.45, 3.60, 3.75, 3.85, 3.93, 4.00, 4.05, 4.10, 4.12, 4.14, 4.16, 4.17, 4.18, 4.19, 4.20, 4.20, 4.21, 4.22, 4.23, 4.24, 4.25]),
        'LI_M_N2_04': np.array([3.00, 3.45, 3.55, 3.70, 3.80, 3.88, 3.95, 4.00, 4.05, 4.08, 4.10, 4.12, 4.13, 4.15, 4.16, 4.17, 4.17, 4.18, 4.19, 4.20, 4.21, 4.22]),
    }

    # Predefined states of charge (soc)
    CHEM_SOC = {
        'LI_FE_P_O4': np.array([0.00, 5.00, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 78.0, 81.0, 84.0, 87.0, 90.0, 92.0, 94.0, 96.0, 97.0, 99.0, 99.5, 100.0]),
        'LI_CO_O2':   np.array([0.00, 5.00, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 78.0, 81.0, 84.0, 87.0, 90.0, 92.0, 94.0, 96.0, 97.0, 99.0, 99.5, 100.0]),
        'LI_M_N2_04': np.array([0.00, 5.00, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 78.0, 81.0, 84.0, 87.0, 90.0, 92.0, 94.0, 96.0, 97.0, 99.0, 99.5, 100.0])
    }

    CHEM_MAX_CYCLES = {
        'LI_FE_P_O4': 4500,
        'LI_CO_O2':   750,
        'LI_M_N2_04': 1500
    }

    def __init__(self, volts: float, amps: float, energy: float, cRating: int, CHEMISTRY_TYPE: str):
        """ Initialize a BatteryCell object.

        Args:
            volts (float): The initial voltage of the battery (in Volts), which sets the state of charge automatically.
            TODO: amps (float): The nominal current of the battery (in Amps).
            energy (float): The nominal energy of the battery (in Watt-hours).
            cRating (int): The C-rating of the battery (unitless), how quickly it can be charged or discharged relative to its capacity.
            CHEMISTRY_TYPE (str): The chemistry type of the battery, defined as a CONSTANT in this BatteryCell.py file

        Raises:
            ValueError: If the chemistry type is not supported.
        """

        if CHEMISTRY_TYPE not in BatteryCell.CHEM_VOLTAGE:
            raise ValueError(f"{CHEMISTRY_TYPE} is an unsupported chemistry. Use 'BatteryCell.LI_FE_P_O4', 'BatteryCell.LI_CO_O2' or 'BatteryCell.LI_M_N2_04'.")
        else:
            self.chemistry = CHEMISTRY_TYPE

        self.cRating = cRating
        self.totalEnergyCapacity = energy

        # See nominal voltages constants in BatteryCell.py
        clampledVoltage = max(min(volts, BatteryCell.CHEM_VOLTAGE[self.chemistry][-1]), BatteryCell.CHEM_VOLTAGE[self.chemistry][0])
        if clampledVoltage != volts:
            raise ValueError(f"{volts} V is out of range for a {self.chemistry} battery chemistry. Valid range is {BatteryCell.CHEM_VOLTAGE[self.chemistry][0]} to {BatteryCell.CHEM_VOLTAGE[self.chemistry][-1]}.")
        else:
            self.currentVoltage = volts
            self.currentAmpere = 0      # Set to zero initially, but updated via BatteryCell.py update_ampere() in Simulation.py run()
            self.stateOfCharge = self.state_of_charge_from_voltage(self.currentVoltage)
            self.currentEnergy = (self.stateOfCharge / 100) * self.totalEnergyCapacity

        self.minVoltage = BatteryCell.CHEM_VOLTAGE[CHEMISTRY_TYPE][0]
        idx = (np.abs(BatteryCell.CHEM_SOC[self.chemistry]- 50)).argmin()           # Array index in CHEM_SOC array closest to 50%
        self.nominalVoltage = BatteryCell.CHEM_VOLTAGE[CHEMISTRY_TYPE][idx]
        self.maxVoltage = BatteryCell.CHEM_VOLTAGE[CHEMISTRY_TYPE][-1]
        self.maxAmpere= cRating *  self.totalEnergyCapacity / self.nominalVoltage   # TODO: Should nominal or current voltage be used here?
        self.maxPower = self.maxVoltage * self.maxAmpere

        self.temperature = 25.0                         # Units are Celsius
        self.health = 100                               # Units are percentage
        self.rechargeCycleNumber = 0                    # Number of time a cell has be recharged


    def __str__(self) -> str:
        """ Output of print() for BatteryCell objects

        Returns:
            str: String representation of the BatteryCell object.
        """

        return f"Battery(V={self.currentVoltage}, A={self.currentAmpere}, Wh={self.totalEnergyCapacity})"

    def consume_energy(self, energy: float):
        """ Subtract energy for energy currently left in the battery cell

        Args:
            energy (float): Energy amount to remove from cell
        """

        self.currentEnergy -= energy
        if self.currentEnergy < 0:
            self.currentEnergy = 0.00
        self.stateOfCharge = self.state_of_charge()

    def energy_capacity(self) -> float:
        """ Calculate the energy capacity left in cell based on state of charge

        Returns:
            float: The energy capacity in Watt-hours (Wh).
        """

        return self.totalEnergyCapacity * self.stateOfCharge

    def state_of_charge(self) -> float:
        """ Exact State of Charge (%) of cell based on energy

        Returns:
            float: The estimated state of charge as percentage from 0% to 100%
        """

        return (self.currentEnergy / self.totalEnergyCapacity) * 100


    def state_of_charge_from_voltage(self, voltage) -> float:
        """ Estimated State of Charge (%) from voltage

        Returns:
            float: The estimated state of charge in percentage.
        """

        return float(np.interp(voltage, BatteryCell.CHEM_VOLTAGE[self.chemistry], BatteryCell.CHEM_SOC[self.chemistry]))


    def recharge(self, finalSoC: float) -> None:
        """ Recharge a battery cell to the desired state of charge.

        Args:
            finalSoC (float): The desired final state of charge

        Raises:
            ValueError: If requested recharge state in equal to or less then current battery state of charge
        """

        if self.stateOfCharge >= finalSoC:
            raise ValueError("Battery already at or above the desired state of recharge.")
        else:
            # Array index in CHEM_SOC array closest to the desired final state of charge
            idx = (np.abs(BatteryCell.CHEM_SOC[self.chemistry]- finalSoC)).argmin()
            self.currentVoltage = BatteryCell.CHEM_VOLTAGE[self.chemistry][idx]
            self.currentPower = self.currentVoltage * self.currentAmpere
            self.rechargeCycleNumber += 1
            self.health = math.exp((math.log(0.8) / self.CHEM_MAX_CYCLES[self.chemistry]) * self.rechargeCycleNumber)
            self.stateOfCharge = finalSoC

    def change_voltage(self, newVoltage: float):
        """ Change voltage directly without simulating a recharge cycle

        Args:
            newVoltage (float):
        """

        self.currentVoltage = newVoltage
        self.stateOfCharge = self.state_of_charge()
        self.currentPower = self.currentVoltage * self.currentAmpere

    def update_ampere(self, loadCurrentDraw: float):
        """ Update per cell current draw and power ouput based on

        Args:
            loadCurrentDraw (float):
        """
        self.currentAmpere = loadCurrentDraw
        self.currentPower = self.currentVoltage * self.currentAmpere


if __name__ == "__main__":
    c18650 = BatteryCell(3.6, 5.0, 20.0, 10, BatteryCell.LI_FE_P_O4)
    print(c18650)
    print(c18650.currentPower)
    print(c18650.nominalVoltage)
    c18650.change_voltage(3.0)
    c18650.recharge(99)
    print(c18650)
