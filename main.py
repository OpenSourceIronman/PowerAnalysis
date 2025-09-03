#!/usr/bin/python3

# External libraries
from nicegui import ui

# Internal libraries
from Simulation import Simulation
from Power.Consumption import Consumption
from Power.BatteryCell import BatteryCell
from Power.BatteryPack import BatteryPack
from PowerModes import PowerModes

DEBUG_STATEMENTS_ON = True

voltageInput = '3.65'
energyInput = '20'
cRatingInput = '1'
chemistryInput = BatteryCell.LI_FE_P_O4
packConfig = ['1S', '1P']

def initialize_data(sim, powermodes: list):
    global voltageInput

    numOfDataPoints = 0
    for i in range(0, len(powermodes), 2):
        numOfDataPoints += powermodes[i+1]

    #sim.batteryPackPercentageLog = [BatteryCell.MAX_STATE_OF_CHARGE] * numOfDataPoints
    sim.batteryPackPercentageLog = [sim.generator.cells.state_of_charge_from_voltage(voltageInput)] * numOfDataPoints
    sim.duration = numOfDataPoints

    return numOfDataPoints

def set_battery_pack_configuration(voltageInput: float, energyInput: float, cRatingInput: int, CHEMISTRY: str):
    global packConfig
    battery = BatteryCell(voltageInput, energyInput, cRatingInput, CHEMISTRY)
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
    global plot, chemistryInput, voltageInput, energyInput, cRatingInput, packConfig

    print(f" Chemistry={chemistryInput}, Voltage={voltageInput}, Energy={energyInput}, CRating={cRatingInput}, PackConfig={packConfig}")

    plot.figure['data'][0]['y'] = sim.run(sim.duration, 95)
    plot.update()

def set_sim_params(sim, powermodes):
    global plot

    initialize_data(sim, powermodes)
    sim.generator = set_battery_pack_configuration(float(voltageInput), float(energyInput), int(cRatingInput), BatteryCell.LI_FE_P_O4)

    plot.figure['data'][0]['y'] = sim.batteryPackPercentageLog
    sim.powermodes = powermodes

    plot.update()

def set_global(name, value):
    globals()[name] = value

    print(f"Updated {name} to {value}")

def update_packConfig(sVal, pVal):
    global packConfig
    if sVal is not None:
        packConfig[0] = sVal
    if pVal is not None:
        packConfig[1] = pVal

    print(f"Updated packConfig: {packConfig}")

def GUI(sim: Simulation, startPoint: int, numOfDataPoints: int) -> None:
    """
        https://fonts.google.com/icons?icon.set=Material+Icons
    """
    global plot, chemistryInput, voltageInput, energyInput, cRatingInput, packConfig

    print("Running GUI function")
    fig = {
        'data': [
            {
                'type': 'scatter',
                'name': 'Battery Simulation',
                'x': list(range(startPoint, startPoint + numOfDataPoints)),
                'y': [BatteryCell.MAX_STATE_OF_CHARGE] * numOfDataPoints
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
        ui.select(["LiFePO4", "LiCoO2", "LiMN2O4", "AGM", "PbA"], value=chemistryInput, on_change=lambda e: set_global("chemistryInput", e.value)).classes('w-max')

        ui.input(label='Battery Cell Voltage (V)', placeholder='Sets State of Charge based on cell chemistry', value=voltageInput, on_change=lambda e: set_global("voltageInput", e.value)).classes('w-1/5')
        ui.input(label='Battery Cell Energy (Wh)', placeholder='Energy capacity of each cell', value=energyInput, on_change=lambda e: set_global("energyInput", e.value)).classes('w-1/5')
        ui.input(label='C-Rating (Unitless charge / discharge rate)', placeholder='Max Amps = C-Rating *  Energy / Voltage', value=cRatingInput, on_change=lambda e: set_global("cRatingInput", e.value)).classes('w-1/5')

        sDropdown = ui.select(["1S", "2S", "3S", "4S"], value="1S",  on_change=lambda e: update_packConfig(e.value, None))
        pDropdown = ui.select(["1P", "2P", "3P", "4P"], value="1P",  on_change=lambda e: update_packConfig(None, e.value))
        packConfig = [sDropdown.value, pDropdown.value]

    with ui.row().classes('w-full'):
        ui.button("Confirm Simulation Parameters", icon='settings', on_click= lambda: set_sim_params(sim, sim.powermodes)).classes('justify-center w-full')
        ui.space().classes('justify-center w-full')
        ui.button("Run Simulation", icon='start', on_click= lambda: run_sim(sim)).props('color=red').classes('justify-center w-full')




if __name__ in {"__main__", "__mp_main__"}:

    motor = Consumption("Motor", 4, 0, 2, 3.125, 100)
    cpu = Consumption("CPU", 2, 0, 2, 3.125, 100)

    submodules = [motor, cpu]

    powerModes = [{motor: Consumption.MAX_POWER_DRAW_MODE,
                    cpu: Consumption.MAX_POWER_DRAW_MODE}, 3600 * Simulation.ONE_SECOND,
                    {motor: Consumption.MAX_POWER_DRAW_MODE,
                    cpu: Consumption.MAX_POWER_DRAW_MODE}, 3600 * Simulation.ONE_SECOND]

    startPoint = 0
    batteryPack = set_battery_pack_configuration(float(voltageInput), float(energyInput), int(cRatingInput), BatteryCell.LI_FE_P_O4)
    sim = Simulation(submodules, batteryPack, powerModes)

    numOfDataPoints = initialize_data(sim, powerModes)
    if DEBUG_STATEMENTS_ON: sim.print_all_sim_objects("Pre GUI")
    GUI(sim, startPoint, numOfDataPoints)

    ui.run(native=True, dark=True, window_size=(1920, 885), title='Battery Simulation')
