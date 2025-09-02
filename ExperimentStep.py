#!/usr/bin/python3

from enum import Enum
#from ExperimentStep import Action, Unit, Step
import re

# https://github.com/pybamm-team/PyBaMM/blob/develop/src/pybamm/experiment/step/base_step.py

examplesExperiments = [
    "Discharge at 1C for 0.5 hours",
    "Discharge at C/20 for 0.5 hours",
    "Charge at 0.5 C for 45 minutes",
    "Discharge at 1 A for 0.5 hours",
    "Charge at 200 mA for 45 minutes",
    "Discharge at 1W for 0.5 hours",
    "Charge at 200mW for 45 minutes",
    "Rest for 10 minutes",
    "Hold at 1V for 20 seconds",
    "Charge at 1 C until 4.1V",
    "Hold at 4.1 V until 50mA",
    "Hold at 3V until C/50",
    "Discharge at C/3 for 2 hours or until 2.5 V"]



class Action(Enum):
    CHARGE = "charge"
    DISCHARGE = "discharge"
    REST = "rest"
    HOLD = "hold"

class Unit(Enum):
    C_RATE = "C"
    AMP = "A"
    WATT = "W"
    WATT_HOUR = "Wh"
    VOLT = "V"

class Step:
    """
    Represents a parsed battery test step.
    """
    def __init__(self, action: Action, value: float, unit: Unit,
                 duration: float, duration_unit: str, until: str):
        self.action = action
        self.value = value
        self.unit = unit
        self.duration = duration
        self.duration_unit = duration_unit
        self.until = until   # e.g. "4.1V", "C/50"

    def __repr__(self):
        return (f"Step(action={self.action}, value={self.value}, unit={self.unit}, "
                f"duration={self.duration} {self.duration_unit}, until={self.until})")

    def parse_instruction(self, text: str):
        """
        Parse an instruction string into a Step object.
        Examples:
            "Discharge at 1C for 0.5 hours"
            "Charge at 0.5 C for 45 minutes"
            "Rest for 10 minutes"
            "Hold at 4.1 V until 50 mA"
        """
        text = text.strip().lower()

        # Detect action
        if text.startswith("discharge"):
            action = Action.DISCHARGE
        elif text.startswith("charge"):
            action = Action.CHARGE
        elif text.startswith("rest"):
            return Step(action=Action.REST,
                        duration=float(re.findall(r"([\d.]+)", text)[0]),
                        duration_unit=text.split()[-1])
        elif text.startswith("hold"):
            action = Action.HOLD
        else:
            raise ValueError(f"Unknown instruction: {text}")

        # Parse "until" conditions
        if "until" in text:
            until = text.split("until")[-1].strip()
            return Step(action=action, until=until)

        # Parse value + unit
        match = re.search(r"at ([\d.]+)\s*([a-zA-Z/]+)", text)
        value, unit = None, None
        if match:
            value = float(match.group(1))
            u = match.group(2)
            if "c" in u:
                unit = Unit.C_RATE
            elif "a" in u and not "ma" in u:
                unit = Unit.AMP
            elif "ma" in u:
                unit = Unit.MILLIAMP
            elif "w" in u and not "mw" in u:
                unit = Unit.WATT
            elif "mw" in u:
                unit = Unit.MILLIWATT
            elif "v" in u:
                unit = Unit.VOLT

        # Parse duration
        duration, duration_unit = None, None
        if "for" in text:
            dur_match = re.search(r"for ([\d.]+)\s*([a-zA-Z]+)", text)
            if dur_match:
                duration = float(dur_match.group(1))
                duration_unit = dur_match.group(2)

        return Step(action=action, value=value, unit=unit,
                    duration=duration, duration_unit=duration_unit)

    def parse_protocol(self, instructions: list):
        """Parse a whole list of instructions into Step objects"""
        return [self.parse_instruction(instr) for instr in instructions]
