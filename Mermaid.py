#!/usr/bin/env python3

from nicegui import ui

# Mermaid: https://docs.mermaidchart.com/mermaid-oss/config/theming.html#flowchart-variables


sankey = """sankey-beta

Pumped heat,"Heating and cooling, homes",193.026
Pumped heat,"Heating and cooling, commercial",70.672"""


with ui.row():
    ui.markdown(f'''
        ```mermaid
        ---
        title: Mermaid
        config:
        theme: 'default'
        themeVariables:
            fontSize: '20px'

        ---
        {sankey}
        ```
    ''', extras=['mermaid']).classes('w-full h-100')

ui.run(native=True, dark=True, window_size=(1080, 720), title='Mermaid Graph', on_air=None)
