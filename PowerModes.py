#!/usr/bin/python3

# Standard libraries
from dataclasses import dataclass, field
import csv

# Internal libraries
from Simulation import Simulation
from Power.Consumption import Consumption


@dataclass
class PowerModes:
    submodules: dict[str, int] = field(default_factory=dict)
    duration : int = Simulation.ONE_SECOND

    def __str__(self) -> str:
        """Custom string formatting: show 0 as a constant string."""
        parts = []

        for name, powerDrawMode in self.submodules.items():
            if powerDrawMode == Consumption.MIN_POWER_DRAW_MODE:
                parts.append(f"{name}: 'MIN_POWER_DRAW_MODE'")
            elif powerDrawMode == Consumption.AVG_POWER_DRAW_MODE:
                parts.append(f"{name}: 'AVG_POWER_DRAW_MODE'")
            elif powerDrawMode == Consumption.MAX_POWER_DRAW_MODE:
                parts.append(f"{name}: 'MAX_POWER_DRAW_MODE'")

        return f"Running {parts} for {self.duration} seconds"


    def add_submodule(self, name: str, powerDrawMode: int = Consumption.MIN_POWER_DRAW_MODE) -> None:
        """ Add """
        self.submodules[name] = powerDrawMode


    def csv_initialization(self, csvFilename: str) -> list:
        """ Initialize power modes from a .csv file

        Args:
            csvFilename (str): Filename of .csv file containing power modes

            Example 0th row of .csv file: "Duration, Submodule Name #1, Current Power Draw Mode #1, ..., Submodule Name #N, Current Power Draw Mode #N"
            Example 1st row of .csv file: "100, Motor, MIN_POWER_DRAW_MODE, CPU, AVG_POWER_DRAW_MODE, Camera, MAX_POWER_DRAW_MODE, LED, MIN_POWER_DRAW_MODE, GPS, AVG_POWER_DRAW_MODE"
            Example 2nd row of .csv file: "200, Motor, AVG_POWER_DRAW_MODE, CPU, AVG_POWER_DRAW_MODE, Camera, MIN_POWER_DRAW_MODE, LED, MIN_POWER_DRAW_MODE, GPS, AVG_POWER_DRAW_MODE"
            Example 3rd row of .csv file: "800, RECHARGE, 99"

        Returns:
            list: List of power modes

            From example:
            [{'Motor': 0, 'CPU': 1, 'Camera': 2, 'LED': 0, 'GPS': 1}, 100, {'Motor': 1, 'CPU': 1, 'Camera': 0, 'LED': 0, 'GPS': 1}, 200, {'RECHARGE': 99}, 800]
        """
        modes = []

        with open(csvFilename, newline="") as f:
                reader = csv.reader(f)

                rowNumber = 0
                for rowData in reader:
                    if rowNumber == 0:
                        pass            # Ignore header row with column names

                    else:
                        timeDuration = int(rowData[0].strip())
                        modes.append(PowerModes(duration= timeDuration * Simulation.ONE_SECOND))

                        for i in range(1, len(rowData), 2):
                            device = rowData[i].strip()
                            if device == "RECHARGE":
                                soc = float(rowData[i+1].strip())
                                modes[rowNumber-1].add_submodule(device, soc)
                            else:
                                POWER_DRAW_MODE = str(rowData[i+1].strip())
                                modes[rowNumber-1].add_submodule(device, self.convert_to_int(POWER_DRAW_MODE))

                    rowNumber += 1

        return modes


    def convert_to_int(self, mode: str):
        """ Converts a string representation of a power draw mode to an integer.

        Args:
            mode (str): A CONSTANT string representation of the power draw mode.

        Returns:
            int: The integer representation of the power draw mode.

        Raises:
            ValueError: If the input string is not a valid power draw mode.
        """
        if mode == "MIN_POWER_DRAW_MODE":
            return 0
        elif mode == "AVG_POWER_DRAW_MODE":
            return 1
        elif mode == "MAX_POWER_DRAW_MODE":
            return 2
        else:
            raise ValueError(f"Invalid power draw mode string value of: {mode}, please check Consumption.py for CONSTANT values")


    def convert_to_string(self, mode: int):
        """ Converts an integer representation of a power draw mode to a string.

        Args:
            mode (int): The Enum like integer representation of the power draw mode.

        Returns:
            str: A CONSTANT string representation of the power draw mode.

        Raises:
            ValueError: If the input integer is not a valid power draw mode.
        """
        if mode == 0:
            return "MIN_POWER_DRAW_MODE"
        elif mode == 1:
            return "AVG_POWER_DRAW_MODE"
        elif mode == 2:
            return "MAX_POWER_DRAW_MODE"
        else:
            raise ValueError(f"Invalid power draw mode integer value of: {mode}, please check Consumption.py for CONSTANT values")


if __name__ == "__main__":
        manualModes = []

        mode1 = PowerModes(duration=3600 * Simulation.ONE_SECOND)
        mode1.add_submodule("Motor")
        mode1.add_submodule("CPU")
        mode1.add_submodule("Camera")
        mode1.add_submodule("LED")
        mode1.add_submodule("GPS")
        manualModes.append(mode1)

        mode2 = PowerModes(duration=3600 * Simulation.ONE_SECOND)
        mode2.add_submodule("Motor", Consumption.AVG_POWER_DRAW_MODE)
        mode2.add_submodule("CPU", Consumption.MAX_POWER_DRAW_MODE)
        mode2.add_submodule("Camera")
        mode2.add_submodule("LED")
        mode2.add_submodule("GPS")
        manualModes.append(mode2)

        #print(manualModes)

        data = PowerModes()
        powerModes = data.csv_initialization("PowerModes.csv")
        print(powerModes[2].submodules)
        print(powerModes[2].duration)
