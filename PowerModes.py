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
            for name, mode in self.submodules.items():
                if mode == Consumption.MIN_POWER_DRAW_MODE:
                    parts.append(f"{name}: 'MIN_POWER_DRAW_MODE'")
                elif mode == Consumption.AVG_POWER_DRAW_MODE:
                    parts.append(f"{name}: 'AVG_POWER_DRAW_MODE'")
                elif mode == Consumption.MAX_POWER_DRAW_MODE:
                    parts.append(f"{name}: 'MAX_POWER_DRAW_MODE'")
            return f"PowerMode({self.duration} seconds of {parts})"

    def add_submodule(self, name: str, mode: int = Consumption.MIN_POWER_DRAW_MODE) -> None:
        """ Add """
        self.submodules[name] = mode
