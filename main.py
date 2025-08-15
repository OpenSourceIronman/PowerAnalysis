#!/.venvPowerAnalysis/bin/python3

from Power.Simulation import Simulation
from Power.Consumption import Consumption
from Power.BatteryCell import BatteryCell
from Power.BatteryPack import BatteryPack

if __name__ == "__main__":
    battery = BatteryCell(3.65, 5.0, 20.0, 10, BatteryCell.LI_FE_P_O4)
    batteryPack = BatteryPack(battery, ['2S', '2P'], 10)

    motor = Consumption("Motor", 48, 0, 5, 10, 100)
    cpu = Consumption("CPU", 5, 0, 2, 5, 100)
    camera = Consumption("Camera", 5, 0, 0.5, 1, 10)

    submodules = [motor, cpu, camera]
    powerModes = [{motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.AVG_POWER_DRAW_MODE,
                   camera: Consumption.MIN_POWER_DRAW_MODE}, 100 * Simulation.ONE_SECOND,

                  {motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.MIN_POWER_DRAW_MODE,
                   camera: Consumption.MIN_POWER_DRAW_MODE}, 200 * Simulation.ONE_SECOND,

                  {motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.MIN_POWER_DRAW_MODE,
                   camera: Consumption.MIN_POWER_DRAW_MODE}, 300 * Simulation.ONE_SECOND]


    sim = Simulation(submodules, batteryPack, 600 * Simulation.ONE_SECOND)
    sim.print_all_sim_objects()
    sim.run(powerModes, 600 * Simulation.ONE_SECOND)
    sim.print_numpy_file(0, 600 * Simulation.ONE_SECOND)
