#!/usr/bin/python3

# External libraries
import sqlite3
from datetime import datetime
from nicegui import Tailwind, ui

# Internal libraries
from Simulation import Simulation
#TODO: from PowerModes import PowerModes
from Power.Consumption import Consumption
from Power.BatteryCell import BatteryCell
from Power.BatteryPack import BatteryPack


DEBUG_STATEMENTS_ON = False

# Global variables initial values for GUI and database table saving
voltageInput = '3.65'
energyInput = '5'
cRatingInput = '10'
chemistryInput = BatteryCell.LI_FE_P_O4
packConfigInput = ['1S', '1P']
efficiencyInput = '95'
saveNumber = 1

def set_battery_pack_parameters(voltageInput: float, energyInput: float, cRatingInput: int, CHEMISTRY_INPUT: str, packConfigInput: list) -> BatteryPack:
    """ Create a new battery pack object with user input values from the GUI.

    Args:
        voltageInput (float): The voltage of a single battery cell in V.
        energyInput (float): The energy capacity of a single battery cell in Wh.
        cRatingInput (int): The unitless C-rating of a single battery cell, which defines the maximum current a cell can output.
        chemistryInput (str): The chemistry of all battery cell(s), must be one of five constants defined in BatteryCell class.
        packConfigInput (list): The series & parellel configuration of battery cells to build a battery pack.

    Returns:
        BatteryPack: An initialized BatteryPack object.
    """
    battery = BatteryCell(voltageInput, energyInput, cRatingInput, CHEMISTRY_INPUT)
    batteryPack = BatteryPack(battery, packConfigInput)

    return batteryPack


def run_sim(sim: Simulation) -> None:
    """ Run simulation defined by GUI inputs and power modes defined in main.py main() function, and then update the graphical plot.

    Args:
        sim (Simulation): The simulation object to run.
    """
    global plot, efficiencyInput

    try:
        plot.figure['data'][0]['y'] = sim.run(sim.experimentDuration, int(efficiencyInput))

    except ValueError as e:
        errorLabel.visible = True
        errorLabel.set_text(f"RUNTIME ERROR: {e}")

    finally:
        plot.update()


def set_sim_params(sim: Simulation) -> None:
    """ Set simulation parameters based on GUI inputs, and determine if the values are valid before running the simulation.

    Args:
        sim (Simulation): The Simulation.py object to set & check parameters for.
    """
    global plot, chemistryInput, voltageInput, energyInput, cRatingInput, packConfig, efficiencyInput, errorLabel

    # Toggle error message off at start of parameter check
    if errorLabel.visible:
        errorLabel.visible = False

    try:
        sim.initialize_data(float(voltageInput))
        sim.valid_dc_dc_voltage_regulator_efficiency(int(efficiencyInput))
        sim.generator = set_battery_pack_parameters(float(voltageInput), float(energyInput), int(cRatingInput), str(chemistryInput), packConfig)
        plot.figure['data'][0]['y'] = sim.batteryPackPercentageLog

    except ValueError as e:
        if DEBUG_STATEMENTS_ON: print("A run time errror occured!")
        errorLabel.visible = True

        msg = str(e)
        if "int()" in msg or "string to float" in msg:
            badValue = msg.split(":")[-1].strip().strip("'")
            if badValue == "":
                badValue = "'    '"
            errorLabel.set_text(f"CONFIG ERROR: You entered {badValue}, which is not a valid integer value.")
        else:
            errorLabel.set_text(f"ERROR: {e}")
        plot.figure['data'][0]['y'] = [sim.generator.cells.state_of_charge_from_voltage(float(voltageInput))] * sim.experimentDuration

    finally:
        plot.update()


def save_data(sim: Simulation) -> None:
    """ Save sim.batteryPackPercentageLog list to auto incrementing tables based on date and time in a SQlite database

    Args:
        sim (Simulation): The simulation object containing the battery pack percentage log.
    """
    # Format as "YYYY_MM_DD_HHMM"
    now = datetime.now()
    timestamp = now.strftime("%Y_%m_%d_%H%M")

    conn = sqlite3.connect('BatteryPackPercentageData.db')
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS BatteryPackPercentageDataTable_{timestamp}
                 (timestamp TEXT, percentage REAL)''')

    for i in range(len(sim.batteryPackPercentageLog)):
        c.execute(f"INSERT INTO BatteryPackPercentageDataTable_{timestamp} VALUES (?, ?)", (str(i), sim.batteryPackPercentageLog[i]))

    conn.commit()
    conn.close()


def set_global(name: str, value) -> None:
    """ Set a global variable to the given value

    Args:
        name (str): The name of the global variable to set.
        value (any): The value to set the global variable to.
    """
    globals()[name] = value
    if DEBUG_STATEMENTS_ON: print(f"Updated {name} to {value}")


def update_pack_config(newValue: str) -> None:
    """ Update the serial (S) and parallel (P) battery pack configuration

    Args:
        newValue (str): The new serial or parallel value to update
    """
    global packConfig

    if "S" in newValue.upper():
        packConfig[0] = newValue
    elif "P" in newValue.upper():
        packConfig[1] = newValue
    else:
        raise ValueError("DEV ERRROR: Invalid GUI input for pack configuration, check GUI() function.")


def GUI(sim: Simulation) -> None:
    """ Define the NiceGUI user interface (plotly graph, text inputs, dropdowns, and buttons)

        NiceGUI framework from https://nicegui.io/
        Icons from https://fonts.google.com/icons?icon.set=Material+Icons

    Args:
        sim (Simulation): Data to display in the GUI.
    """
    global plot, chemistryInput, voltageInput, energyInput, cRatingInput, packConfig, efficiencyInput, errorLabel

    fig = {
        'data': [
            {
                'type': 'scatter',
                'name': 'Battery Simulation',
                'x': list(range(0, sim.experimentDuration)),
                'y': [BatteryCell.MAX_STATE_OF_CHARGE] * sim.experimentDuration,  # Initial chart shall display 100% state of charge
                'line': {'width': 4}
            },
        ],
        'layout': { # https://plotly.com/python/reference/layout/#layout-paper_bgcolor
            'margin': {'l': 60, 'r': 60, 't': 30, 'b': 75},
            'plot_bgcolor':  '#4d4d4d',
            'paper_bgcolor': '#4d4d4d',
            'xaxis': {
                'title': {'text': 'Time (in Seconds)'},
                'gridcolor': 'white',
                'color': 'white',

            },
            'yaxis': {
                'title': {'text': 'Battery State of Charge (SoC) (as %)'},
                'gridcolor': 'white',
                'color': 'white',
                'range': [0, BatteryCell.MAX_STATE_OF_CHARGE]
            },
        },
    }

    # Show only one zero (for Y-axis) in lower left corner of graph to make it look nicer, and set X-axis to 2 minute intervals
    fig['layout']['xaxis'].update({
        'tickmode': 'array',
        'tickvals': [v for v in range(120, sim.experimentDuration, 120)],
    })

    plot = ui.plotly(fig).classes('w-full h-100')

    with ui.row().classes('w-full'):
        ui.select(["LiFePO4", "LiCoO2", "LiMN2O4", "AGM", "PbA"], value=chemistryInput, on_change=lambda e: set_global("chemistryInput", e.value)).classes('w-max')

        ui.input(label='Single Battery Cell Voltage (V)', placeholder='Sets State of Charge (SoC) based on cell chemistry', value=voltageInput, on_change=lambda e: set_global("voltageInput", e.value)).classes('w-1/5')
        ui.input(label='Single Battery Cell Energy (Wh)', placeholder='Energy capacity of each cell', value=energyInput, on_change=lambda e: set_global("energyInput", e.value)).classes('w-1/5')
        ui.input(label='C-Rating (Unitless charge / discharge rate)', placeholder='Max Amps = C-Rating *  Energy / Voltage', value=cRatingInput, on_change=lambda e: set_global("cRatingInput", e.value)).classes('w-1/5')
        ui.input(label='DC/DC Efficiency (%)', placeholder='DC/DC Voltage Regulator Efficiency', value=efficiencyInput, on_change=lambda e: set_global("efficiencyInput", e.value)).classes('w-1/5')

        sDropdown = ui.select(["1S", "2S", "3S", "4S", "5S", "6S"], value="1S",  on_change=lambda e: update_pack_config(e.value))
        pDropdown = ui.select(["1P", "2P", "3P", "4P", "5P", "6P"], value="1P",  on_change=lambda e: update_pack_config(e.value))
        packConfig = [sDropdown.value, pDropdown.value]

    with ui.row().classes('w-full'):
        ui.button("Confirm Parameters & Reset Graph", icon='settings', on_click= lambda: set_sim_params(sim)).props('color=orange').classes('justify-center w-full')
        ui.space().classes('justify-center w-full')
        ui.button("Run Simulation", icon='start', on_click= lambda: run_sim(sim)).props('color=green').classes('justify-center w-full')
        ui.space().classes('justify-center w-full')
        ui.button("Save Simulation to SQLite Database", icon='save', on_click= lambda: save_data(sim)).props('color=blue').classes('justify-center w-full')
        ui.space().classes('justify-center w-full')

        redLabelStyle = Tailwind().text_color('red-600').font_weight('bold')
        errorLabel = ui.label('').classes('text-center w-full text-lg')
        errorLabel.visible = False
        redLabelStyle.apply(errorLabel)


if __name__ in {"__main__", "__mp_main__"}:

    motor = Consumption("Motor", 4, 0, 2, 3.125, 100)
    cpu = Consumption("CPU", 2, 0, 2, 3.125, 100)

    submodules = [motor, cpu]

    powerModes = [{motor: Consumption.MAX_POWER_DRAW_MODE,
                   cpu: Consumption.MAX_POWER_DRAW_MODE}, 1200 * Simulation.ONE_SECOND,
                  {motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.AVG_POWER_DRAW_MODE}, 1200 * Simulation.ONE_SECOND,
                  {motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.MIN_POWER_DRAW_MODE}, 1200 * Simulation.ONE_SECOND,
                  BatteryCell.RECHARGE,                   20]

    batteryPack = set_battery_pack_parameters(float(voltageInput), float(energyInput), int(cRatingInput), str(chemistryInput), list(packConfigInput))
    sim = Simulation(submodules, batteryPack, powerModes)
    sim.initialize_data(float(voltageInput))
    if DEBUG_STATEMENTS_ON: sim.print_all_sim_objects("Pre GUI")

    GUI(sim)

    ui.run(native=True, dark=True, window_size=(1920, 885), title='Battery Pack Simulation', on_air=False)
