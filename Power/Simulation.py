#!/.venvPowerAnalysis/bin/python3

# External libraries
import numpy as np

# Internal libraries
from Power.Consumption import Consumption
from Power.BatteryPack import BatteryPack

class Simulation:

    BATTERY_DATA_NUMPY_NPY_FILE = "BatteryDataLog.npy"

    ONE_SECOND = 1
    ONE_HOUR_IN_SECONDS = 3600
    HALF_HOUR_IN_SECONDS = int(ONE_HOUR_IN_SECONDS / 2)
    QUARTER_HOUR_IN_SECONDS = int(ONE_HOUR_IN_SECONDS / 4)
    TEN_MINUTE_IN_SECONDS = int(ONE_HOUR_IN_SECONDS / 6)
    FIVE_MINUTE_IN_SECONDS = int(ONE_HOUR_IN_SECONDS / 12)

    def __init__(self, powerDrawSources: list[Consumption], powerGenerationSource: BatteryPack, timeInSeconds: int):
        """ Simulates the power consumption and generation of a system over a given time period.

        Args:
            submodule (Submodule): The submodule to simulate.
            timeInSeconds (int): The duration in seconds for which the simulation is run.

        Returns:
            float: The total energy consumed by the submodule in Watt-hours (Wh).
        """
        self.consumers = powerDrawSources
        self.generator = powerGenerationSource
        self.timeInSeconds = timeInSeconds


    def run(self, powermodes: list, runTimeInSeconds: int):
        """ Runs the simulation and collect data on battery charge state

        Args:
            powermodes (list): Power modes to simulate with the follwoing types [dict, duration, ..., dict, duration, dict, duration]
            runTimeInSeconds (int): The duration in seconds for which the simulation is run.

        Returns:
            float: The total energy consumed by all submodule in Watt-hours (Wh).
        """

        # Create NumPy array filled with initial battery percentage
        batteryPercentageLog = np.full(runTimeInSeconds, self.generator.soc, dtype=np.float32)

        totalPowerModeTime = 0
        for i in range(0, len(powermodes), 2):
            totalPowerModeTime += powermodes[i+1]

        if totalPowerModeTime != runTimeInSeconds:
            print(f"Requested simulation time of {runTimeInSeconds}, doesn't match time defined in the powermodes variable")

        timeIndex = 0
        for i in range(0, len(powermodes), 2):
            energyUsed = 0
            timeDuration = powermodes[i+1]
            for t in range(timeDuration):
                for consumer in self.consumers:
                    consumer.turn_on(powermodes[i][consumer])
                    energyUsed += consumer.real_time_energy(Simulation.ONE_SECOND)
                self.generator.cell.consume_energy(energyUsed / (self.generator.seriesCount * self.generator.parallelCount))
                batteryPercentageLog[timeIndex] = round(self.generator.cell.state_of_charge(), 2)
                timeIndex += 1

        np.save(self.BATTERY_DATA_NUMPY_NPY_FILE, batteryPercentageLog)


    def print_all_sim_objects(self):
        print("Simulation SubModules:")

        for consumer in self.consumers:
            print(f"  {consumer.__class__.__name__}.py: {consumer}")

        print(f"  {self.generator.__class__.__name__}.py: {self.generator}")


    def print_numpy_file(self, start: int, numberOfDataPoints: int):
        arr = np.load(Simulation.BATTERY_DATA_NUMPY_NPY_FILE)
        print(f"{arr[start:(start + numberOfDataPoints)]} has length of {len(arr)}")
