#!/.venvPowerAnalysis/bin/python3

from nicegui import ui

from Power.Simulation import Simulation
from Power.Consumption import Consumption
from Power.BatteryCell import BatteryCell
from Power.BatteryPack import BatteryPack


def GUI(startPoint, numOfDataPoints):
    global energyInput, voltageInput, cRatingInput

    ui.dark_mode().enable()

    fig = {
        'data': [
            {
                'type': 'scatter',
                'name': 'Battery Simulation',
                'x': list(range(startPoint, startPoint + numOfDataPoints)),
                'y': sim.convert_numpy_file_to_list(startPoint, numOfDataPoints),
            },
        ],
        'layout': { # https://plotly.com/python/reference/layout/#layout-paper_bgcolor
            'margin': {'l': 60, 'r': 60, 't': 30, 'b': 75},
            'plot_bgcolor': '#4d4d4d',
            'paper_bgcolor' : '#4d4d4d',
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


    ui.plotly(fig).classes('w-full h-100')


    with ui.row():
        voltageInput = ui.input(label='Battery Voltage', placeholder='in units of Volts')
        energyInput = ui.input(label='Battery Energy', placeholder='in units of Wh')
        cRatingInput = ui.input(label='C-Rating', placeholder='How quickly it can be charged / discharged ')

    ui.button("Run Simulation").classes('w-full h-100')


if __name__ in {"__main__", "__mp_main__"}:


    battery = BatteryCell(3.65, 5.0, 1.25, 10, BatteryCell.LI_FE_P_O4)
    batteryPack = BatteryPack(battery, ['2S', '2P'])

    motor = Consumption("Motor", 48, 0, 1, 5, 100)
    cpu = Consumption("CPU", 5, 0, 2, 5, 100)
    camera = Consumption("Camera", 5, 0, 0.5, 1, 10)

    submodules = [motor, cpu, camera]
    powerModes = [{motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.AVG_POWER_DRAW_MODE,
                   camera: Consumption.MIN_POWER_DRAW_MODE}, 100 * Simulation.ONE_SECOND,

                  {motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.MIN_POWER_DRAW_MODE,
                   camera: Consumption.MIN_POWER_DRAW_MODE}, 100 * Simulation.ONE_SECOND,

                  {motor: Consumption.MIN_POWER_DRAW_MODE,
                   cpu: Consumption.MIN_POWER_DRAW_MODE,
                   camera: Consumption.MIN_POWER_DRAW_MODE}, 100 * Simulation.ONE_SECOND]

    sim = Simulation(submodules, batteryPack)
    sim.print_all_sim_objects()
    sim.run(powerModes, 300 * Simulation.ONE_SECOND)
    #sim.print_numpy_file(0, 300 * Simulation.ONE_SECOND)

    startPoint = 0
    numOfDataPoints = 300 * Simulation.ONE_SECOND
    GUI(startPoint, numOfDataPoints)
    ui.run(native=True, window_size=(1920, 885), title='Battery Simulation')
