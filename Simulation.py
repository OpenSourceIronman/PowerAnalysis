#!/.venvPowerAnalysis/bin/python3

# External libraries
import numpy as np

# Internal libraries
from Power.Consumption import Consumption
from Power.BatteryPack import BatteryPack
from Power.BatteryCell import BatteryCell

class Simulation:

    BATTERY_DATA_NUMPY_NPY_FILE = "BatteryDataLog.npy"

    ONE_SECOND = 1
    ONE_HOUR_IN_SECONDS = 3600
    HALF_HOUR_IN_SECONDS = int(ONE_HOUR_IN_SECONDS / 2)
    QUARTER_HOUR_IN_SECONDS = int(ONE_HOUR_IN_SECONDS / 4)
    TEN_MINUTE_IN_SECONDS = int(ONE_HOUR_IN_SECONDS / 6)
    FIVE_MINUTE_IN_SECONDS = int(ONE_HOUR_IN_SECONDS / 12)

    def __init__(self, powerDrawSources: list[Consumption], powerGenerationSource: BatteryPack, modes: list):
        """ Simulates the power consumption and generation of a system over a given time period.

        Args:
            powerDrawSources (Consumption): A list of submodules to simulate.
            powerGenerationSource (BatteryPack): The battery pack to simulate.
            modes (list): Power modes to simulate even indexes are Dictionaries and old modes are Intergers

        Returns:
            float: The total energy consumed by the submodule in Watt-hours (Wh).
        """
        self.consumers = powerDrawSources
        self.generator = powerGenerationSource
        self.powermodes = modes
        self.experimentDuration = self.calculate_duration(modes)
        self.batteryPackPercentageLog = [BatteryCell.MAX_STATE_OF_CHARGE] * self.experimentDuration
        #print(self.batteryPackPercentageLog)

    def calculate_duration(self, modes: list) -> int:
        totalDuration = 0
        for i in range(0, len(modes), 2):
            totalDuration += modes[i+1]

        return totalDuration

    def run(self, runTimeInSeconds: int, voltageRegulatorEfficiency: int):
        """ Runs the simulation and collect data on battery charge state

        Args:
            runTimeInSeconds (int): The duration in seconds for which the simulation is run.
            voltageRegulatorEfficiency (int): The efficiency of the voltage regulator in percentage from 25% to 99%

        Returns:
            NOTHING
        """
        self.batteryPackPercentageLog = [BatteryCell.MAX_STATE_OF_CHARGE] * self.experimentDuration

        if self.experimentDuration < runTimeInSeconds:
            raise ValueError(f"Requested simulation time of {runTimeInSeconds}, is more than time defined in the powermodes variable.")

        if voltageRegulatorEfficiency < 25 or voltageRegulatorEfficiency > 99:
            raise ValueError("Voltage regulator efficiency must be between 25% and 99%, unless you have a very bad or physics breaking regulator :)")

        timeIndex = 0
        totalElaspedTime = 0
        for i in range(0, len(self.powermodes), 2):
            energyUsed = 0
            timeDuration = self.powermodes[i+1]

            # Only simulate until we hit runTimeInSeconds
            stepsToRun = min(timeDuration, runTimeInSeconds - totalElaspedTime)

            for t in range(stepsToRun):
                totalCurrentDraw = 0
                energyUsed = 0
                for consumer in self.consumers:

                    if self.powermodes[i] == BatteryCell.RECHARGE:
                        #print(f"Charging from {self.generator.cells.stateOfCharge} to {self.powermodes[i+1]}")
                        self.generator.cells.recharge(self.powermodes[i+1])
                    else:
                        consumer.turn_on(self.powermodes[i][consumer])
                        totalCurrentDraw += consumer.current
                        energyUsed += consumer.real_time_energy(Simulation.ONE_SECOND)

                #print(f"Update Ampere Draw: {totalCurrentDraw / self.generator.parallelCount}")
                self.generator.cells.update_ampere(totalCurrentDraw / self.generator.parallelCount)
                #print(f"Energy Used Per Cell: {energyUsed / (self.generator.seriesCount * self.generator.parallelCount)}")
                self.generator.cells.consume_energy(energyUsed / (self.generator.seriesCount * self.generator.parallelCount))

                totalPowerDraw = 0
                for consumer in self.consumers:
                    totalPowerDraw += consumer.power

                effectivePowerOutput = self.generator.maxPackPower * (voltageRegulatorEfficiency / 100)
                if totalPowerDraw > effectivePowerOutput:
                    raise ValueError(f"Warning: Total power draw of {totalPowerDraw} Watts, exceeds battery pack capacity of {effectivePowerOutput} Watts")

                self.batteryPackPercentageLog[timeIndex] = self.generator.cells.state_of_charge()
                #print(f"Battery Pack Percentage: {self.batteryPackPercentageLog[timeIndex]}")
                timeIndex += 1

            totalElaspedTime += stepsToRun
            if totalElaspedTime > runTimeInSeconds:
                break

        return self.batteryPackPercentageLog


    def print_all_sim_objects(self, adjective: str):
        print(f"{adjective} Simulation SubModules:")

        for consumer in self.consumers:
            print(f"    {consumer.__class__.__name__}.py: {consumer}")

        print(f"    {self.generator.__class__.__name__}.py: {self.generator}")


    def print_numpy_file(self, start: int, numberOfDataPoints: int):

        np.set_printoptions(suppress=True)  # disables scientific notation
        np.set_printoptions(precision=2)    # optional: sets decimal places
        arr = np.load(Simulation.BATTERY_DATA_NUMPY_NPY_FILE)
        print(f"{arr[start:(start + numberOfDataPoints)]} has length of {len(arr)}")

if __name__ == "__main__":
    motor = Consumption("Motor", 4, 0, 2, 3.125, 100)
    cpu = Consumption("CPU", 2, 0, 2, 3.125, 100)

    submodules = [motor, cpu]

    powerModes = [{motor: Consumption.MAX_POWER_DRAW_MODE,
                   cpu: Consumption.MAX_POWER_DRAW_MODE}, 1200 * Simulation.ONE_SECOND,
                  {motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.AVG_POWER_DRAW_MODE}, 1200 * Simulation.ONE_SECOND,
                  {motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.MIN_POWER_DRAW_MODE}, 1200 * Simulation.ONE_SECOND,
                  BatteryCell.RECHARGE, 100]

    battery = BatteryCell(3.65, 20, 1, BatteryCell.LI_FE_P_O4)
    batteryPack = BatteryPack(battery, ['1P','2S'])

    simulation = Simulation(submodules, batteryPack, powerModes)
    simulation.print_all_sim_objects("Starting")

    log = simulation.run(3600 * Simulation.ONE_SECOND, 90)
    simulation.print_all_sim_objects("Ending")
