#!/.venvPowerAnalysis/bin/python3

class Consumption:

    MIN_POWER_DRAW_MODE = 0
    AVG_POWER_DRAW_MODE = 1
    MAX_POWER_DRAW_MODE = 2


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

        self.packSOC = 100

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
            float: The total energy consumed in Watt-hours (Wh)
        """
        energy = 0.0
        for timestep in range(timeInSeconds):
            energy += self.voltage * self.current * (self.dutyCycle / 100) * (1.0 / 3600)

        return energy


    def turn_on(self, mode):
        """ Turns on the submodule and sets the current draw (and thus power) based on the specified mode.

        Args:
            mode (str): The power draw mode to use.
        """
        self.on = True

        if mode == self.MIN_POWER_DRAW_MODE:
            self.current = self.minCurrent
        elif mode == self.AVG_POWER_DRAW_MODE:
            self.current = self.averageCurrent
        elif mode == self.MAX_POWER_DRAW_MODE:
            self.current = self.maxCurrent

        self.power = self.voltage * self.current


    def turn_off(self):
        """ Turns off the module and sets the current draw (and thus power) to zero.
        """
        self.on = False
        self.current = 0.0
