#!/.venvPowerAnalysis/bin/python3

# Python standard library
from datetime import datetime, timedelta

# External libraries
import numpy as np

# Internal libraries
from Power.Generation import Generation
from Power.Consumption import Consumption


class Simulation:
    """ Simulates the power consumption and generation of a system over a given time period.

    Args:
        submodule (Submodule): The submodule to simulate.
        timeInSeconds (int): The duration in seconds for which the simulation is run.

    Returns:
        float: The total energy consumed by the submodule in Watt-hours (Wh).
    """
    def __init__(self, powerDrawSources: list[Consumption], powerGenerationSources: list[Generation], timeInSeconds: int):
        self.consumers = powerDrawSources
        self.generators = powerGenerationSources
        self.timeInSeconds = timeInSeconds


    def run(self, initialBatteryPercentage: float, timeInSeconds: int):
        """ Runs the simulation and collect data on battery charge state

        Returns:
            float: The total energy consumed by the submodule in Watt-hours (Wh).
        """
        # Sum up total energy storage in units of Wh for all generators
        totalEnergyStorage = sum(generator.energyCapacity for generator in self.generators)


        # Create NumPy array filled with 100.0%
        batteryPercentage = np.full(timeInSeconds, 100.0, dtype=np.float32)

        # Parameters
        startTime = datetime.now()

        # Timestamps as numpy array of datetime64[ns]
        timestamps = np.array([startTime + timedelta(seconds=i) for i in range(timeInSeconds)], dtype='datetime64[s]')

        # Combine into structured NumPy array
        batteryLog = np.zeros(timeInSeconds, dtype=[('time', 'datetime64[s]'), ('percent', 'f4')])
        batteryLog['time'] = timestamps
        batteryLog['percent'] = batteryPercentage





        energyUsed = 0
        currentEnergy = totalEnergyStorage
        for _ in range(self.timeInSeconds):
            energyUsed += self.consumers.real_time_energy(1)
            currentEnergy -= energyUsed

        return energy / 3600


        np.save("BatteryDataLog.npy", batteryLog)
