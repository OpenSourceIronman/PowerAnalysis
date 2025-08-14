#!/.venvPowerAnalysis/bin/python3

from Power.Simulation import Simulation
from Power.Generation import Generation
from Power.Consumption import Consumption

import numpy as np

if __name__ == "__main__":
    batteryCell = Generation()
    motor = Consumption("Motor", 48, 0, 5, 10, 100)
    cpu = Consumption("CPU", 5, 0, 2, 5, 100)
    camera = Consumption("Camera", 5, 0, 0.5, 1, 10)

    batteryPack = Generation(batteryCell, ('2S', '2P'))
    submodules = [motor, cpu, camera]
    powerModes = [{motor: Consumption.MAX_POWER_DRAW_MODE,
                   cpu: Consumption.MAX_POWER_DRAW_MODE,
                   camera: Consumption.MAX_POWER_DRAW_MODE},

                  {motor: Consumption.AVG_POWER_DRAW_MODE,
                   cpu: Consumption.AVG_POWER_DRAW_MODE,
                   camera: Consumption.AVG_POWER_DRAW_MODE},

                  {motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.MIN_POWER_DRAW_MODE,
                   camera: Consumption.MIN_POWER_DRAW_MODE}]


    sim = Simulation(submodules, batteryPack, Consumption.ONE_HOUR_IN_SECONDS)
    # sim.print_all_sim_objects()
    sim.run(powerModes, Generation.MAX_STATE_OF_CHARGE, (3 * Consumption.ONE_SECOND))
    #sim.print_numpy_file(0, 10)
