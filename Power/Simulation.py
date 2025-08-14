#!/.venvPowerAnalysis/bin/python3

# External libraries
import numpy as np

# Internal libraries
from Power.Generation import Generation
from Power.Consumption import Consumption


class Simulation:

    NUMPY_NPY_FILE = "BatteryDataLog.npy"

    def __init__(self, powerDrawSources: list[Consumption], powerGenerationSources: list[Generation], timeInSeconds: int):
        """ Simulates the power consumption and generation of a system over a given time period.

        Args:
            submodule (Submodule): The submodule to simulate.
            timeInSeconds (int): The duration in seconds for which the simulation is run.

        Returns:
            float: The total energy consumed by the submodule in Watt-hours (Wh).
        """
        self.consumers = powerDrawSources
        self.generators = powerGenerationSources
        self.timeInSeconds = timeInSeconds


    def run(self, powermodes: list[dict], initialBatteryPercentage: float, runTimeInSeconds: int):
        """ Runs the simulation and collect data on battery charge state

        Returns:
            float: The total energy consumed by all submodule in Watt-hours (Wh).
        """
        # Sum up total energy storage in units of Wh for all generators
        totalEnergyStorage = sum(generator.energyCapacity for generator in self.generators)

        # Create NumPy array filled with initial battery percentage
        batteryPercentage = np.full(runTimeInSeconds, initialBatteryPercentage, dtype=np.float32)

        energyUsed = 0
        currentEnergy = totalEnergyStorage
        print(f"TimeInSeconds: {runTimeInSeconds}")
        for i in range(runTimeInSeconds):
            for consumer in self.consumers:
                consumer.turn_on(powermodes[i][consumer])
                energyUsed += consumer.real_time_energy(Consumption.ONE_SECOND)
                currentEnergy -= energyUsed
                currentBatteryPercentage = currentEnergy/totalEnergyStorage
                batteryPercentage[i] = currentBatteryPercentage

        np.save(self.NUMPY_NPY_FILE, batteryPercentage)


    def print_all_sim_objects(self):
        print("Simulation SubModules:")

        for consumer in self.consumers:
            print(f"  {consumer.__class__.__name__}.py: {consumer}")

        for generator in self.generators:
            print(f"  {generator.__class__.__name__}.py: {generator}")


    def print_numpy_file(self, start: int, numberOfDataPoints: int):
        arr = np.load(Simulation.NUMPY_NPY_FILE)
        print(arr[start:(start + numberOfDataPoints)])
