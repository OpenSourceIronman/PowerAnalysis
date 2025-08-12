from Power.Simulation import Simulation
from Power.Generation import Generation
from Power.Consumption import Consumption


if __name__ == "__main__":
    battery = Generation()
    motor = Consumption("Motor", 48, 0, 5, 10, 100)
    cpu = Consumption("CPU", 5, 0, 2, 5, 100)
    camera = Consumption("Camera", 5, 0, 0.5, 1, 10)

    p2s2BatteryPack = [battery, battery, battery, battery]
    submodules = [motor, cpu, camera]

    sim = Simulation(submodules, p2s2BatteryPack, Consumption.ONE_HOUR_IN_SECONDS)
