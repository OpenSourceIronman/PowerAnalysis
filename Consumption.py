#!/usr/bin/env python3

class Consumption:


    def __init__(self, name:str, volts:float, minAmps:float, avgAmps:float, maxAmps:float, duty:float):
        """ Initializes a Consumption object.

        Args:
            name (str): The name of the power draw module.
            volts (float): The voltage of the power draw module.
            minAmps (float): The minimum current draw of the power draw module.
            avgAmps (float): The average current draw of the power draw module.
            maxAmps (float): The maximum current draw of the power draw module.
            duty (float): The duty cycle of the power draw module.
        """
        self.name = name

        # Real time volts and amps
        self.voltage = volts                       # Units are Volts (V)
        self.current = avgAmps                     # Units are Amps (A)

        # Preset values for different power modes
        self.minCurrent = minAmps
        self.averageCurrent = avgAmps
        self.maxCurrent = maxAmps

        self.power = self.voltage * self.current   # Units are Watts (W)
        self.dutyCycle = duty                      # Units are percent (0-100%)
        self.on = False                            # Units are Boolean (True/False)


    def __str__(self):
        """ Returns a string representation of the power draw object.
        """
        return f"{self.name}(voltage={self.voltage}, current={self.current}, power={self.power}, dutyCycle={self.dutyCycle}, on={self.on})"


    def real_time_power(self):
        """ Calculates the instantaneous power consumption of a submodule.

        Returns:
            float: The current power consumption in Watts (W).
        """
        return self.voltage * self.current


    def real_time_energy(self, timeInSeconds: int):
        """ Calculates the energy consumed by a submodule over a given time period.

        Args:
            timeInSeconds (int): The duration in seconds for which the energy consumption is calculated.

        Returns:
            float: The total energy consumed in Watt-hours (Wh) rounded to 3 decimal places.
        """
        energy = 0.0
        for timestep in range(timeInSeconds):
            energy += self.voltage * self.current * (self.dutyCycle / 100) * (1.0 / 3600)

        return round(energy, 3)
