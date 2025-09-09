#!/usr/bin/python3

# Standard libraries
from dataclasses import dataclass, field
from typing import Dict

# Internal libraries
from Simulation import Simulation
from Power.Consumption import Consumption

@dataclass
class PowerModes:
    submodules: Dict[str, int] = field(default_factory=dict)
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
            return f"PowerMode({self.duration} seconds of {parts})"

    def add_submodule(self, name: str, powerDrawMode: int = Consumption.MIN_POWER_DRAW_MODE) -> None:
        """ Add """
        self.submodules[name] = powerDrawMode

    def initialize_power_modes(self, cvsInput):
        modes = []


        # TODO: Use a .csv file to set power modes
        # Example 1st row of .csv file: "100, Motor, MIN_POWER_DRAW_MODE, CPU, AVG_POWER_DRAW_MODE, Camera, MAX_POWER_DRAW_MODE, LED, MIN_POWER_DRAW_MODE, GPS, AVG_POWER_DRAW_MODE"
        # Example 2nd row of .csv file: "200, Motor, AVG_POWER_DRAW_MODE, CPU, AVG_POWER_DRAW_MODE, Camera, MIN_POWER_DRAW_MODE, LED, MIN_POWER_DRAW_MODE, GPS, AVG_POWER_DRAW_MODE"

        cvsList = cvsRowInput.split(',')
        for i in range(1, len(cvsList), 2):
            name = cvsList[i]
            mode = cvsList[i+1]
            dict = {name: mode}
            self.add_submodule(name, mode)

        mode1 = PowerModes(duration=100 * Simulation.ONE_SECOND)
        mode1.add_submodule("Motor")
        mode1.add_submodule("CPU")
        mode1.add_submodule("Camera")
        mode1.add_submodule("LED")
        mode1.add_submodule("GPS")
        modes.append(mode1)

        mode2 = PowerModes(duration=200 * Simulation.ONE_SECOND)
        mode2.add_submodule("Motor", Consumption.AVG_POWER_DRAW_MODE)
        mode2.add_submodule("CPU", Consumption.MAX_POWER_DRAW_MODE)
        mode2.add_submodule("Camera")
        mode2.add_submodule("LED")
        mode2.add_submodule("GPS")
        modes.append(mode2)

        return modes
