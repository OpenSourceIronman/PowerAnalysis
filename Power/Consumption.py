#!/usr/bin/python3

class Consumption:

    MIN_POWER_DRAW_MODE = 0
    AVG_POWER_DRAW_MODE = 1
    MAX_POWER_DRAW_MODE = 2

    def __init__(self, name: str, volts: float, minAmps: float, avgAmps: float, maxAmps: float, duty: float):
        """ Initializes a Consumption object with it turned on by default.

        Args:
            name (str): Human readable name of the power draw module used when printing usinf print().
            volts (float): The required voltage of the power draw module.
            minAmps (float): The minimum current draw of a power draw Consumption object when on.
            avgAmps (float): The average current draw of a power draw Consumption object when on.
            maxAmps (float): The maximum current draw of a power draw Consumption object when on.
            duty (float): The on duty cycle of a power draw Consumption object.
        """
        self.name = name

        # Preset values for different power modes
        if minAmps < 0 or avgAmps < 0 or maxAmps < 0:
            raise ValueError("Minimum, average, and maximum current draw values must be non-negative")
        elif minAmps > avgAmps or avgAmps > maxAmps or minAmps > maxAmps:
            raise ValueError("Minimum current draw must be less than average current draw, which must be less than maximum current draw")
        else:
            self.minCurrent = minAmps
            self.averageCurrent = avgAmps
            self.maxCurrent = maxAmps


        # Real time volts and amps
        self.voltage = volts                        # Units are Volts (V)
        self.current = avgAmps                      # Units are Amps (A)
        self.power = self.voltage * self.current    # Units are Watts (W)

        self.dutyCycle = 0
        self.set_duty_cycle(duty)                   # Units are percent (0-100%)
        self.deviceOn = True                        # Units are Boolean (True/False)


    def __str__(self):
        """ Returns a string representation of a Consumption object.
        """
        return f"{self.name}(voltage={self.voltage}, current={self.current}, power={self.power}, dutyCycle={self.dutyCycle}%, on={self.deviceOn})"


    def real_time_power(self):
        """ Calculates the instantaneous power consumption of a submodule.

        Returns:
            float: The current power consumption in Watts (W).
        """
        if not self.deviceOn:
            return 0.0

        return self.voltage * self.current


    def real_time_energy(self, timeInSeconds: int):
        """ Calculates the energy consumed by a submodule over a given time period.

        Args:
            timeInSeconds (int): The duration in seconds for which the energy consumption is calculated.

        Returns:
            float: The total energy consumed in Watt-hours (Wh)
        """
        totalEnergyConsumed = 0.0

        if not self.deviceOn:
            return 0.0

        for timestep in range(timeInSeconds):
            totalEnergyConsumed += self.voltage * self.current * (self.dutyCycle / 100.0) * (1.0 / 3600)

        return totalEnergyConsumed


    def turn_on(self, mode):
        """ Turns on the submodule and sets the current draw (and thus power) based on the specified mode.

        Args:
            mode (str): The power draw mode to use.
        """
        self.deviceOn = True

        if mode == self.MIN_POWER_DRAW_MODE:
            self.current = self.minCurrent
        elif mode == self.AVG_POWER_DRAW_MODE:
            self.current = self.averageCurrent
        elif mode == self.MAX_POWER_DRAW_MODE:
            self.current = self.maxCurrent
        else:
            raise ValueError("Invalid power draw mode, use either MIN_POWER_DRAW_MODE, AVG_POWER_DRAW_MODE, or MAX_POWER_DRAW_MODE")

        self.power = self.voltage * self.current


    def turn_off(self):
        """ Turns off the module and sets the current draw (and thus power) to zero.
        """
        self.deviceOn = False
        self.current = 0.0
        self.power = 0.0

    def set_duty_cycle(self, dutyCycle: float):
        if dutyCycle < 0 or dutyCycle > 100:
            raise ValueError("Duty cycle must be between 0 and 100")

        self.dutyCycle = dutyCycle
        self.power = self.voltage * self.current * (self.dutyCycle / 100.0)
