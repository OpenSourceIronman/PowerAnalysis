#!/usr/bin/python3

# Internal libraries
from Power.Consumption import Consumption
from Power.BatteryPack import BatteryPack
from Power.BatteryCell import BatteryCell

class Simulation:

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


    def initialize_data(self, voltageInput: float):
        """ Initialize data logging list for battery charge state

        Args:
            voltageInput (float): Initial voltage from GUI (and thus state of charge) to start the simulation.
        """
        self.batteryPackPercentageLog = [self.generator.cells.state_of_charge_from_voltage(voltageInput)] * self.experimentDuration


    def calculate_duration(self, modes: list) -> int:
        """ Calculate the total duration of a simulation experiment based on the "Power Modes" data structure

        Args:
            modes (list): List of power modes to run eash submodule and their durations

        Returns:
            int: Total duration of the simulation in seconds
        """
        totalDuration = 0
        for i in range(0, len(modes), 2):
            totalDuration += modes[i+1]

        return totalDuration


    def valid_dc_dc_voltage_regulator_efficiency(self, efficiencyInput: int) -> bool:
        """ Validate the efficiency of a DC to DC voltage regulator between battery pack and all submodules

        Args:
            efficiencyInput (int): The rough efficiency of a DC to DC voltage regulator between battery pack all submodules

        Returns:
            bool: True if the efficiency is valid, False otherwise
        """
        isValid = False

        # No power conversion is 100% (that is physics breaking) and most linear regulator are better then 25%
        if efficiencyInput < 25 or efficiencyInput > 99:
            isValid = False
            raise ValueError("DC-DC voltage regulator efficiency must be > 24% and < 100%.")
        else:
            isValid = True

        return isValid


    def run(self, runTimeInSeconds: int, voltageRegulatorEfficiency: int) -> list:
        """ Runs the simulation and collects data on battery charge state

        Args:
            runTimeInSeconds (int): The duration in seconds for which the simulation is run.
            voltageRegulatorEfficiency (int): Rough efficiency of a DC to DC voltage regulator (see Simulation.valid_dc_dc_voltage_regulator_efficiency() for valid values)

        Returns:
            list: Battery charge state data calculated during a simulation run.
        """
        self.batteryPackPercentageLog = [BatteryCell.MAX_STATE_OF_CHARGE] * self.experimentDuration

        if self.experimentDuration < runTimeInSeconds:
            raise ValueError(f"Requested simulation time of {runTimeInSeconds}, is more than time defined in the powermodes variable.")


        # Initialize timeIndex & totalElaspedTime to 1 at start of the first power mode to log state of charge before sim starts
        timeIndex = 1
        totalElaspedTime = 1

        # Every even index in the powermodes list data structure defines a time length in seconds or recharge percentage
        for i in range(0, len(self.powermodes), 2):
            timeDuration = self.powermodes[i+1]

            # Allow For Loop to exit early if "runTimeInSecond"s is reached, before "timeDuration" defined in powermodes ends
            timeStepsToRun = min(timeDuration, runTimeInSeconds - totalElaspedTime)

            for _ in range(timeStepsToRun):
                totalCurrentDraw = 0
                energyUsed = 0
                for consumer in self.consumers:

                    # Determine if "powermodes" data structure defines a charging or power consuming cycle
                    if self.powermodes[i] == BatteryCell.RECHARGE:
                        print(f"Charging from {self.generator.cells.stateOfCharge} to {self.powermodes[i+1]}")
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

            totalElaspedTime += timeStepsToRun
            if totalElaspedTime > runTimeInSeconds:
                break

        return self.batteryPackPercentageLog


    def print_all_sim_objects(self, adjective: str):
        """ Prints all sub-objects instances within a Simulation.py object with their respective classes names.

        Args:
            adjective (str): Useful adjective to describe the state of all the simulation submodules at time of print() statement.
        """
        print(f"{adjective} Simulation SubModules:")

        for consumer in self.consumers:
            print(f"    {consumer.__class__.__name__}.py: {consumer}")

        print(f"    {self.generator.__class__.__name__}.py: {self.generator}")


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

    battery = BatteryCell(3.65, 9, 1, BatteryCell.LI_FE_P_O4)
    batteryPack = BatteryPack(battery, ['1P','2S'])

    simulation = Simulation(submodules, batteryPack, powerModes)
    simulation.print_all_sim_objects("Starting")

    log = simulation.run(3600 * Simulation.ONE_SECOND, 90)
    simulation.print_all_sim_objects("Ending")
