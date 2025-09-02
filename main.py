#!/usr/bin/python3

# External libraries
from nicegui import ui
import numpy as np

# Internal libraries
from Simulation import Simulation
from Power.Consumption import Consumption
from Power.BatteryCell import BatteryCell
from Power.BatteryPack import BatteryPack
from PowerModes import PowerModes

DEBUG_STATEMENTS_ON = True

voltageInput = '3.65'
energyInput = '5'
cRatingInput = '10'
chemistryInput = BatteryCell.LI_FE_P_O4
packConfig = ['1S', '1P']

def initialize_data(sim, powermodes: list):
    numOfDataPoints = 0
    for i in range(0, len(powermodes), 2):
        numOfDataPoints += powermodes[i+1]

    sim.batteryPackPercentageLog = [BatteryCell.MAX_STATE_OF_CHARGE] * numOfDataPoints
    sim.duration = numOfDataPoints
    print(f"# of data points: {sim.duration}")
    return numOfDataPoints

def set_battery_pack_configuration(voltageInput: float, energyInput: float, cRatingInput: int, CHEMISTRY: str):
    global packConfig
    battery = BatteryCell(voltageInput, 0, energyInput, cRatingInput, CHEMISTRY)
    batteryPack = BatteryPack(battery, packConfig)

    return batteryPack

def set_power_modes():
    modes = []

    mode1 = PowerModes(duration=100 * Simulation.ONE_SECOND)
    mode1.add_submodule("Motor")
    mode1.add_submodule("CPU")
    mode1.add_submodule("Camera")
    mode1.add_submodule("LED")
    mode1.add_submodule("GPS")
    modes.append(mode1)

    mode2 = PowerModes(duration=200 * Simulation.ONE_SECOND)
    mode2.add_submodule("Motor", Consumption.AVG_POWER_DRAW_MODE)
    mode2.add_submodule("CPU", Consumption.MAX_POWER_DRAW_MODE)
    mode2.add_submodule("Camera")
    mode2.add_submodule("LED")
    mode2.add_submodule("GPS")
    modes.append(mode2)

    return modes

def run_sim(sim):
    global plot

    sim.run(sim.duration)

    newY = sim.batteryPackPercentageLog
    plot.figure['data'][0]['y'] = newY

    plot.update()

def restart_sim(sim, powermodes):
    global plot

    initialize_data(sim, powermodes)
    newY = sim.batteryPackPercentageLog
    plot.figure['data'][0]['y'] = newY
    sim.powermodes = powermodes

    plot.update()

def GUI(sim: Simulation, startPoint: int, numOfDataPoints: int) -> None:
    """
        https://fonts.google.com/icons?icon.set=Material+Icons
    """
    global energyInput, voltageInput, cRatingInput, chemistryInput, packConfig, plot

    print("Running GUI function")
    fig = {
        'data': [
            {
                'type': 'scatter',
                'name': 'Battery Simulation',
                'x': list(range(startPoint, startPoint + numOfDataPoints)),
                'y': sim.batteryPackPercentageLog
            },
        ],
        'layout': { # https://plotly.com/python/reference/layout/#layout-paper_bgcolor
            'margin': {'l': 60, 'r': 60, 't': 30, 'b': 75},
            'plot_bgcolor':  '#4d4d4d',
            'paper_bgcolor': '#4d4d4d',
            'xaxis': {
                'title': {'text': 'Time (seconds)'},
                'gridcolor': 'white',
                'color': 'white',

            },
            'yaxis': {
                'title': {'text': 'Battery SOC (%)'},
                'gridcolor': 'white',
                'color': 'white',
                'range': [0, 100]
            },
        },
    }

    plot = ui.plotly(fig).classes('w-full h-100')

    with ui.row().classes('w-full'):
        ui.select(["LiFePO4", "LiCoO2", "LiMN2O4"], value=chemistryInput).classes('w-max')

        ui.input(label='Battery Cell Voltage (V)', placeholder='Sets State of Charge based on cell chemistry', value=voltageInput).classes('w-1/5')
        ui.input(label='Battery Cell Energy (Wh)', placeholder='Energy capacity of each cell', value=energyInput).classes('w-1/5')
        ui.input(label='C-Rating (Unitless charge / discharge rate)', placeholder='Max Amps = C-Rating *  Energy / Voltage', value=cRatingInput).classes('w-1/5')

        sDropdown = ui.select(["1S", "2S", "3S", "4S"], value="1S")
        pDropdown = ui.select(["1P", "2P", "3P", "4P"], value="1P")
        packConfig = [sDropdown.value, pDropdown.value]

    with ui.row().classes('w-full'):
        ui.button("Run Simulation", icon='start', on_click= lambda: run_sim(sim)).classes('justify-center w-full')
        ui.button("Restart Simulation", icon='clear', on_click= lambda: restart_sim(sim, sim.powermodes)).classes('justify-center w-full')


if __name__ in {"__main__", "__mp_main__"}:

    motor = Consumption("Motor", 5, 0, 1, 2, 100)
    cpu = Consumption("CPU", 6, 0, 0.5, 5, 100)
    camera = Consumption("Camera", 1, 0, 1, 1, 10)

    submodules = [motor, cpu, camera]
    #TODO: set_power_modes()
    powerModes = [{motor: Consumption.AVG_POWER_DRAW_MODE,
                   cpu: Consumption.MIN_POWER_DRAW_MODE,
                   camera: Consumption.MIN_POWER_DRAW_MODE}, 60 * Simulation.ONE_SECOND]


    startPoint = 0
    batteryPack = set_battery_pack_configuration(float(voltageInput), float(energyInput), int(cRatingInput), BatteryCell.LI_FE_P_O4)
    sim = Simulation(submodules, batteryPack, powerModes)
    sim.unit_test()

    numOfDataPoints = initialize_data(sim, powerModes)
    if DEBUG_STATEMENTS_ON: sim.print_all_sim_objects()
    GUI(sim, startPoint, numOfDataPoints)

    ui.run(native=True, dark=True, window_size=(1920, 885), title='Battery Simulation')
