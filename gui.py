import PySimpleGUI as sg
# from mqtt2 import esp_start_transmittion, esp_stop_transmittion, CLST
# import matplotlib.pyplot as plt 
sg.theme("GreenTan")

tab1_layout =  [[sg.Text('Nothing here')]]

tab2_layout = [
    [
        sg.Button("Start", key="start"),
        sg.Button("Stop", key="stop")
    ]
]

      
layout = [
    [sg.Text('ECG & PPG monitor', size=(40, 1), justification='center', font='Helvetica 20')],
    [
        sg.TabGroup([
            [
                sg.Tab('Monitor', tab1_layout),
                sg.Tab('Setting', tab2_layout)
            ]
        ])
    ] 
]

# create the window and show it without the plot

window = sg.Window('Project3C2', layout, finalize=True)
# needed to access the canvas element prior to reading the window

while True:
    event, values = window.read()
    if event == 'Exit' or event == sg.WIN_CLOSED:
        break

    # if event == "start":
    #     esp_start_transmittion()

    # if event == "stop":
    #     esp_stop_transmittion()
        
    
window.close()