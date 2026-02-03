#!/usr/bin/python3

# External libraries
import sqlite3
from typing import BinaryIO
from datetime import datetime
from nicegui import Tailwind, ui

# Internal libraries
from Simulation import Simulation
from PowerModes import PowerModes
from Power.Consumption import Consumption
from Power.BatteryCell import BatteryCell
from Power.BatteryPack import BatteryPack


# Global variables initial values for GUI and debugging
DEBUG_STATEMENTS_ON = False

voltageInput = '3.65'
energyInput = '5.0'
cRatingInput = '10'
chemistryInput = BatteryCell.LI_FE_P_O4
packConfigInput = ['1S', '1P']
efficiencyInput = '95'
powerModesInput = []

#errorLabel = ""

csvHelp ="""
Duration, Name #1, Power Draw Mode #1, ... , ..., Name #N, Power Draw Mode #N

100, Motor, MIN_POWER_DRAW_MODE, CPU, AVG_POWER_DRAW_MODE, Camera, MAX_POWER_DRAW_MODE, LED, MIN_POWER_DRAW_MODE, GPS, AVG_POWER_DRAW_MODE

200, Motor, AVG_POWER_DRAW_MODE, CPU, AVG_POWER_DRAW_MODE, Camera, MIN_POWER_DRAW_MODE, LED, MIN_POWER_DRAW_MODE, GPS, AVG_POWER_DRAW_MODE

800, RECHARGE, 99
"""


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


def run_sim(sim: Simulation, plot) -> None:
    """ Run simulation defined by GUI inputs and power modes defined in main.py main() function, and then update the graphical plot.

    Args:
        sim (Simulation): The simulation object to run.
    """
    global efficiencyInput

    try:
        plot.figure['data'][0]['y'] = sim.run(sim.experimentDuration, int(efficiencyInput))

    except ValueError as e:
        errorLabel.visible = True
        errorLabel.set_text(f"RUNTIME ERROR: {e}")
        plot.figure['data'][0]['y'] = [0] * sim.experimentDuration

    finally:
        plot.update()


def set_sim_params(sim: Simulation, plot) -> None:
    """ Set simulation parameters based on GUI inputs, and determine if the values are valid before running the simulation.

    Args:
        sim (Simulation): The Simulation.py object to set & check parameters for.
    """
    global chemistryInput, voltageInput, energyInput, cRatingInput, packConfigInput, efficiencyInput, errorLabel

    # Toggle error message off at start of parameter check
    if errorLabel.visible:
        errorLabel.visible = False

    try:
        sim.initialize_data(float(voltageInput))
        sim.valid_dc_dc_voltage_regulator_efficiency(int(efficiencyInput))
        sim.generator = set_battery_pack_parameters(float(voltageInput), float(energyInput), int(cRatingInput), str(chemistryInput), packConfigInput)
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
            errorLabel.set_text(f"CONFIG ERROR: {e}")
        #TODO REMOVE? plot.figure['data'][0]['y'] = [sim.generator.cells.state_of_charge_from_voltage(float(voltageInput))] * sim.experimentDuration

    finally:
        plot.update()


def process_csv_upload(content: BinaryIO): # -> list:
    """ Read uploaded .csv content and process rows.

    Args:
        content (BinaryIO): The uploaded CSV content.

    Returns:
        list: The processed rows.
    """
    global powerModesInput
    data = PowerModes()
    powerModesObjList = data.csv_initialization("PowerModes.csv")
    #print(f"1st Power Mode Submodules: {powerModesObjList[2].submodules}")
    #print(f"1st Power Mode Duration: {powerModesObjList[2].duration}")
    powerModesInput = []
    for powerMode in powerModesObjList:
        powerModesInput.append(powerMode.submodules)
        powerModesInput.append(powerMode.duration)
        #print(f"Power Mode Submodules: {powerMode.submodules}")
        #print(f"Power Mode Duration: {powerMode.duration}")

    print(powerModesInput)
    #return convert_power_modes(powerModesObjList)


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
    global packConfigInput

    if "S" in newValue.upper():
        packConfigInput[0] = newValue
    elif "P" in newValue.upper():
        packConfigInput[1] = newValue
    else:
        raise ValueError("DEV ERRROR: Invalid GUI input for pack configuration, check GUI() function.")


def GUI(sim: Simulation) -> None:
    """ Define the NiceGUI user interface (plotly graph, text inputs, dropdowns, file upload, and buttons)

        NiceGUI framework from https://nicegui.io/
        Icons from https://fonts.google.com/icons?icon.set=Material+Icons

    Args:
        sim (Simulation): Data to display in the GUI.
    """
    global plot, chemistryInput, voltageInput, energyInput, cRatingInput, packConfigInput, efficiencyInput, errorLabel

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

    fig['layout']['yaxis'].update({
        'tickmode': 'array',
        'tickvals': list(range(0, int(BatteryCell.MAX_STATE_OF_CHARGE + 1), 10)),
    })

    plot = ui.plotly(fig).classes('w-full h-[500px] relative z-0')

    with ui.dialog() as dialog, ui.card().classes("w-max"):#.classes("w-[900px] max-w-[95%]"):  # 👈 make dialog wider:
        ui.label("Example .csv file structure").classes("text-xl font-bold")
        ui.label(csvHelp).classes("text-md whitespace-pre-wrap")  # preserve formatting
        ui.button("Close", on_click=dialog.close).classes("w-full")

    with ui.row().classes('justify-center w-full'):
        ui.select(["LiFePO4", "LiCoO2", "LiMN2O4", "AGM", "PbA"], value=chemistryInput, on_change=lambda e: set_global("chemistryInput", e.value)).classes('w-max')

        ui.input(label='Single Battery Cell Voltage (V)', placeholder='Sets State of Charge % based on cell chemistry', value=voltageInput, on_change=lambda e: set_global("voltageInput", e.value)).classes('w-1/6')
        ui.input(label='Single Battery Cell Energy (Wh)', placeholder='Energy capacity of each cell', value=energyInput, on_change=lambda e: set_global("energyInput", e.value)).classes('w-1/6')
        ui.input(label='C-Rating (Charge / Discharge Rate)', placeholder='Max Amps = C-Rating *  Energy / Voltage', value=cRatingInput, on_change=lambda e: set_global("cRatingInput", e.value)).classes('w-1/6')
        ui.input(label='DC/DC Efficiency (%)', placeholder='DC/DC Voltage Regulator Efficiency', value=efficiencyInput, on_change=lambda e: set_global("efficiencyInput", e.value)).classes('w-1/6')

        sDropdown = ui.select(["1S", "2S", "3S", "4S", "5S", "6S"], value="1S",  on_change=lambda e: update_pack_config(e.value))
        pDropdown = ui.select(["1P", "2P", "3P", "4P", "5P", "6P"], value="1P",  on_change=lambda e: update_pack_config(e.value))
        packConfigInput = [sDropdown.value, pDropdown.value]


    with ui.row().classes('justify-center w-full gap-4 items-center'):
        ui.upload(label="Upload PowerModes.csv file to define power consuming submodules and recharge cycles in this simulation", on_upload=lambda e: process_csv_upload(e.content), auto_upload=True, on_rejected=lambda: ui.notify('File Rejected, select and upload the "PowerModes.csv" file only!')).props('accept=PowerModes.csv color=orange').classes('w-1/2')

        ui.button("Confirm Parameters, Reset Graph, & Reset Error Messages ", icon='settings', on_click= lambda: set_sim_params(sim, plot)).props('color=orange').classes('justify-center w-full')
        ui.space().classes('justify-center w-full')
        ui.button("Run Simulation", icon='start', on_click= lambda: run_sim(sim, plot)).props('color=green').classes('justify-center w-full')
        ui.space().classes('justify-center w-full')
        ui.button("Save Simulation to SQLite Database", icon='save', on_click= lambda: save_data(sim)).props('color=blue').classes('justify-center w-full')
        #ui.space().classes('justify-center w-full')

        redLabelStyle = Tailwind().text_color('red-600').font_weight('bold')
        errorLabel = ui.label('').classes('text-center w-full text-lg')
        errorLabel.visible = False
        redLabelStyle.apply(errorLabel)

        ui.space().classes('justify-center w-full')
        ui.button("Help", icon='help', on_click=dialog.open).props('color=red').classes('w-1/4 h-14')


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
                  {BatteryCell.RECHARGE: 69.0},           400 * Simulation.ONE_SECOND]

    batteryPack = set_battery_pack_parameters(float(voltageInput), float(energyInput), int(cRatingInput), str(chemistryInput), list(packConfigInput))
    sim = Simulation(submodules, batteryPack, powerModes)
    sim.initialize_data(float(voltageInput))
    if DEBUG_STATEMENTS_ON: sim.print_all_sim_objects("Pre GUI")

    #set_app_dock_icon()
    GUI(sim)

    ui.run(native=True, dark=True, window_size=(1920, 1080), title='Battery Pack Simulation', on_air=None)
