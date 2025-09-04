#!/usr/bin/python3

# External libraries
import numpy as np

class BatteryCell:

    MAX_STATE_OF_CHARGE = 100.0       # Units are in perentage
    RECHARGE = "RECHARGE"

    # Battery cell chemistry types
    LI_FE_P_O4 = 'LiFePO4'  # Lithium Iron Phosphate
    LI_CO_O2 = 'LiCoO2'     # Lithium Cobalt Oxide
    LI_M_N2_04 = 'LiMN2O4'  # Lithium Manganese Dioxide
    PB_A = 'PbA'            # Lead Acid
    AGM = 'AGM'             # Absorbed Glass Mat

    # Cell voltages for different chemistries at predefined state of charge (SoC) percentages (see CHEM_SOC)
    CHEM_VOLTAGE = {
        'LiFePO4': np.array([2.80, 2.90, 3.00, 3.08, 3.12, 3.16, 3.20, 3.24, 3.28, 3.30, 3.32, 3.34, 3.36, 3.38, 3.40, 3.42, 3.44, 3.48, 3.50, 3.55, 3.60, 3.65]),
        'LiCoO2':  np.array([3.00, 3.45, 3.60, 3.75, 3.85, 3.93, 4.00, 4.05, 4.10, 4.12, 4.14, 4.16, 4.17, 4.18, 4.19, 4.20, 4.20, 4.21, 4.22, 4.23, 4.24, 4.25]),
        'LiMN2O4': np.array([3.00, 3.45, 3.55, 3.70, 3.80, 3.88, 3.95, 4.00, 4.05, 4.08, 4.10, 4.12, 4.13, 4.15, 4.16, 4.17, 4.17, 4.18, 4.19, 4.20, 4.21, 4.22]),
        'AGM':     np.array([1.75, 1.90, 1.98, 2.02, 2.05, 2.07, 2.09, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18, 2.19, 2.20, 2.21, 2.22, 2.23, 2.25, 2.27]),
        'PbA':     np.array([1.70, 1.85, 1.93, 1.98, 2.00, 2.02, 2.04, 2.06, 2.08, 2.09, 2.10, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18, 2.20, 2.22, 2.24])
    }

    # Predefined states of charge, with same step percentages for consistency and easier interpolation
    CHEM_SOC = {
        'LiFePO4':  np.array([0.00, 5.00, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 78.0, 81.0, 84.0, 87.0, 90.0, 92.0, 94.0, 96.0, 97.0, 99.0, 99.5, 100.0]),
        'LiCoO2':   np.array([0.00, 5.00, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 78.0, 81.0, 84.0, 87.0, 90.0, 92.0, 94.0, 96.0, 97.0, 99.0, 99.5, 100.0]),
        'LiMN2O4':  np.array([0.00, 5.00, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 78.0, 81.0, 84.0, 87.0, 90.0, 92.0, 94.0, 96.0, 97.0, 99.0, 99.5, 100.0]),
        'AGM':      np.array([0.00, 5.00, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 78.0, 81.0, 84.0, 87.0, 90.0, 92.0, 94.0, 96.0, 97.0, 99.0, 99.5, 100.0]),
        'PbA':      np.array([0.00, 5.00, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 78.0, 81.0, 84.0, 87.0, 90.0, 92.0, 94.0, 96.0, 97.0, 99.0, 99.5, 100.0])
    }

    # Typical values if cell cycle cyxcled to less than 50% depth-of-discharge (DOD)
    CHEM_MAX_CYCLES = {
        'LiFePO4': 4500,
        'LiCoO2':   750,
        'LiMN2O4': 1500,
        'AGM':      600,
        'PbA':      300
    }

    def __init__(self, volts: float, energy: float, cRating: int, CHEMISTRY_TYPE: str):
        """ Initialize a BatteryCell object.

        Args:
            volts (float): The initial voltage of a battery cell (in Volts), which sets the state of charge automatically.
            energy (float): The NOMINAL total energy capacity (nominal voltage (in Volts) * capacity (in Ah)) of a battery cell (in Watt-hours).
            cRating (int): The C-rating of a battery cell (unitless), how quickly it can be charged or discharged relative to its capacity.
            CHEMISTRY_TYPE (str): The chemistry type of a battery cell, defined as a CONSTANT in this BatteryCell.py file.

        Raises:
            ValueError: If the chemistry type is not supported.
        """
        # Set currentAmpere and thus currentPower to zero initially, but updated via BatteryCell.py update_ampere() in Simulation.py run()
        self.currentAmpere = 0
        self.currentPower = 0

        if CHEMISTRY_TYPE not in BatteryCell.CHEM_VOLTAGE:
            raise ValueError(f"{CHEMISTRY_TYPE} is an unsupported chemistry. Use 'BatteryCell.LI_FE_P_O4', 'BatteryCell.LI_CO_O2' or 'BatteryCell.LI_M_N2_04'.")
        else:
            self.chemistry = CHEMISTRY_TYPE

        if cRating < 0:
            raise ValueError("Battery cell C-Rating must be non-negative.")
        else:
            self.cRating = cRating


        # See nominal voltages constants at top of BatteryCell.py file
        clampledVoltage = max(min(volts, BatteryCell.CHEM_VOLTAGE[self.chemistry][-1]), BatteryCell.CHEM_VOLTAGE[self.chemistry][0])
        if clampledVoltage != volts:
            raise ValueError(f"{volts} V is out of range for a {self.chemistry} battery chemistry. Valid range is {BatteryCell.CHEM_VOLTAGE[self.chemistry][0]} to {BatteryCell.CHEM_VOLTAGE[self.chemistry][-1]}.")
        else:
            self.currentVoltage = volts
            self.stateOfCharge = self.state_of_charge_from_voltage(self.currentVoltage)
            self.totalEnergyCapacity = energy
            self.currentEnergy = (self.stateOfCharge / 100) * self.totalEnergyCapacity

        self.minVoltage = BatteryCell.CHEM_VOLTAGE[CHEMISTRY_TYPE][0]
        idx = (np.abs(BatteryCell.CHEM_SOC[self.chemistry]- 50)).argmin()           # Array index in CHEM_SOC array closest to 50%
        self.nominalVoltage = BatteryCell.CHEM_VOLTAGE[CHEMISTRY_TYPE][idx]
        self.maxVoltage = BatteryCell.CHEM_VOLTAGE[CHEMISTRY_TYPE][-1]
        self.maxAmpere= cRating *  self.totalEnergyCapacity / self.nominalVoltage
        self.maxPower = self.maxVoltage * self.maxAmpere

        self.temperature = 25.0                         # Units are Celsius
        self.health = 100                               # Units are percentage
        self.rechargeCycleNumber = 0                    # Number of time a cell has be recharged

        self.currentDrawSet = False


    def __str__(self) -> str:
        """ print() output for BatteryCell objects

        Returns:
            str: String representation of the BatteryCell object.
        """

        return f"BatteryCell(V={self.currentVoltage}, A={self.currentAmpere}, Wh={self.totalEnergyCapacity}, C-Rating={self.cRating}, Chemistry={self.chemistry})"

    # Less than
    def __lt__(self, other):
        return self.currentVoltage < other.currentVoltage

   # Greater than
    def __gt__(self, other):
        return self.currentVoltage > other.currentVoltage

    # Less than or equal to
    def __le__(self, other):
        return self.currentVoltage <= other.currentVoltage

    # Greater than or equal to
    def __ge__(self, other):
        return self.currentVoltage >= other.currentVoltage

    # Equal to
    def __eq__(self, other):
        return self.currentVoltage == other.currentVoltage


    def energy_capacity(self) -> float:
        """ Calculate the energy capacity left in cell based on state of charge

        Returns:
            float: The energy capacity in Watt-hours (Wh).
        """

        return self.totalEnergyCapacity * (self.stateOfCharge / 100)


    def state_of_charge(self) -> float:
        """ Exact State of Charge (%) of cell based on energy

        Returns:
            float: The estimated state of charge as percentage from 0% to 100%
        """

        return (self.currentEnergy / self.totalEnergyCapacity) * 100


    def state_of_charge_from_voltage(self, voltage) -> float:
        """ Estimated State of Charge (%) from the cell voltage level

        Returns:
            float: The estimated state of charge in percentage from 0% to 100%
        """

        return float(np.interp(voltage, BatteryCell.CHEM_VOLTAGE[self.chemistry], BatteryCell.CHEM_SOC[self.chemistry]))


    def consume_energy(self, energy: float) -> None:
        """ Subtract energy for energy currently left in the battery cell

        Args:
            energy (float): Energy amount to remove from cell
        """
        if not self.currentDrawSet:
            raise ValueError("Battery cell current draw not set in BatteryCell.update_ampere() before Simulator.run() called.")

        self.currentEnergy -= energy
        if self.currentEnergy < 0:
            self.currentEnergy = 0.00

        # Array index in CHEM_SOC array closest to the current state of charge
        idx = (np.abs(BatteryCell.CHEM_SOC[self.chemistry] - self.stateOfCharge)).argmin()
        self.currentVoltage = BatteryCell.CHEM_VOLTAGE[self.chemistry][idx]
        self.currentPower = self.currentVoltage * self.currentAmpere

        self.stateOfCharge = self.state_of_charge()


    def recharge(self, finalSoC: float) -> None:
        """ Recharge a battery cell to the desired state of charge.

        Args:
            finalSoC (float): The desired final state of charge

        Raises:
            ValueError: If requested recharge state in equal to or less then current battery state of charge
        """
        #print(f"Recharging... {self.stateOfCharge} upto {finalSoC}")
        if self.stateOfCharge > BatteryCell.MAX_STATE_OF_CHARGE:
            raise ValueError("Can't recharge battery cell above 100%")
        else:
            # Array index in CHEM_SOC array closest to the desired final state of charge
            idx = (np.abs(BatteryCell.CHEM_SOC[self.chemistry]- finalSoC)).argmin()
            self.currentVoltage = BatteryCell.CHEM_VOLTAGE[self.chemistry][idx]
            self.currentPower = self.currentVoltage * self.currentAmpere
            self.currentEnergy = self.totalEnergyCapacity * (finalSoC / 100)
            self.health = np.exp((np.log(0.8) / self.CHEM_MAX_CYCLES[self.chemistry]) * self.rechargeCycleNumber)

            # If depth-of-discharge (DOD) is less than 50% then increment the recharge cycle number
            if self.stateOfCharge <= 50:
                self.rechargeCycleNumber += 1

            self.stateOfCharge = finalSoC


    def change_voltage(self, newVoltage: float) -> None:
        """ Change voltage directly without simulating a recharge cycle

        Args:
            newVoltage (float):
        """

        self.currentVoltage = newVoltage
        self.stateOfCharge = self.state_of_charge()
        self.currentPower = self.currentVoltage * self.currentAmpere


    def update_ampere(self, loadCurrentDraw: float) -> None:
        """ Update per cell requested current draw and power output

        Args:
            loadCurrentDraw (float): Current draw in amps defined by the external Consumption.py object(s)
        """
        self.currentDrawSet = False
        if loadCurrentDraw > self.maxAmpere:
            self.currentAmpere = self.maxAmpere
            raise ValueError(f"Current draw of {loadCurrentDraw} exceeds maximum limit of {self.maxAmpere} for the battery cell(s)")
        else:
            self.currentDrawSet = True
            self.currentAmpere = loadCurrentDraw

        self.currentPower = self.currentVoltage * self.currentAmpere


if __name__ == "__main__":
    c18650 = BatteryCell(3.6, 2.0, 10, BatteryCell.LI_FE_P_O4)
    print(c18650)
    print(f"Instant Power = {c18650.currentPower} Watts")
    print(f"Max Power = {c18650.maxPower} Watts")
    print(f"SOC = {c18650.stateOfCharge}%")
    c18650.change_voltage(2.0)
    c18650.recharge(100)
    print(c18650)
