import paho.mqtt.client as mqtt
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
from spo2 import R
import json

fname = "data_eyeta.txt"
f = open(fname,'w')
f.write("")
f.close()

size = 1000
x_vec = np.linspace(0,1,size+1)[0:-1]
temp = [[0]*size]*3
y_vec = np.array(temp)
line = []
c = 0
r = []
ir = []

# def CLST():
#     client.loop_stop()

def live_plotter(x_vec,y_data,line,identifier='',pause_time=0.00000001):
    if line==[]:
        line = [[],[],[]]
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig, ax = plt.subplots(1, 2)
        # create a variable for the line so we can later update it
        line[0], = ax[0].plot(x_vec, y_data[0], c = "red")
        line[1], = ax[0].plot(x_vec, y_data[1], c = "black")

        line[2], = ax[1].plot(x_vec, y_data[2], c = "green")
        #update plot label/title
        plt.ylabel('Y Label')
        plt.title('Title: {}'.format(identifier))
        plt.show()
    
    # after the figure, axis, and line are created, we only need to update the y-data
    line[0].set_ydata(y_data[0])
    line[1].set_ydata(y_data[1])
    line[2].set_ydata(y_data[2])

    data_mutual_min = np.min([np.min(y_data[0]), np.min(y_data[1])])
    data_mutual_max = np.max([np.max(y_data[0]), np.max(y_data[1])])
    data_mutual_std = (np.std(y_data[0])+np.std(y_data[1]))/2

    ylim_mutual_min = np.min([line[0].axes.get_ylim()[0], line[1].axes.get_ylim()[0]])
    ylim_mutual_max = np.max([line[0].axes.get_ylim()[1], line[1].axes.get_ylim()[1]])

    # adjust limits if new data goes beyond bounds
    if data_mutual_min <= ylim_mutual_min or data_mutual_max >= ylim_mutual_max:
        # line[0].axes.set_ylim(temp)
        line[1].axes.set_ylim([data_mutual_min + data_mutual_std, data_mutual_max + data_mutual_std])
        line[0].axes.set_ylim([data_mutual_min + data_mutual_std, data_mutual_max + data_mutual_std])

    if np.min(y_data[2])<=line[2].axes.get_ylim()[0] or np.max(y_data[2])>=line[2].axes.get_ylim()[1]:
        line[2].axes.set_ylim([np.min(y_data[2])-np.std(y_data[2]),np.max(y_data[2])+np.std(y_data[2])])

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    
    # return line so we can update it again in the next iteration
    return line

def ppg_setting():
    """
    led     : "ledBrightness" :   Options: 0=Off to 255=50mA \n
    savg    : "sampleAverage" :   Options: 1, 2, 4, 8, 16, 32 \n
    mode    : "ledMode"       :   Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green \n
    sr      : "sampleRate"    :   Options: 50, 100, 200, 400, 800, 1000, 1600, 3200 \n
    pwm     : "pulseWidth"    :   Options: 69, 118, 215, 411 \n
    range   : "adcRange"      :   Options: 2048, 4096, 8192, 16384 \n
    """
    setting_dict = {
        "ledBrightness" : 70, #Options: 0=Off to 255=50mA
        "sampleAverage" : 1,  #Options: 1, 2, 4, 8, 16, 32
        "ledMode" : 2,        #Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
        "sampleRate" : 400,  #Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
        "pulseWidth" : 215,   #Options: 69, 118, 215, 411
        "adcRange" : 16384   #Options: 2048, 4096, 8192, 16384
    }
    setting_json = json.dumps(setting_dict)
    client.publish("esp32/ppg_setting", setting_json)

def esp_start_transmittion():
    client.publish("esp32/start", "just some text it doesn't matter")

def esp_stop_transmittion():
    client.publish("esp32/stop", "just some text it doesn't matter")

def data(message):
    global y_vec, line, x_vec, c, r, ir

    samples = str(message.payload.decode("utf-8")).split('END')[0].split('#')
    
    f = open(fname,'a+')
    l = []
    for sample in samples:
            if len(sample) != 0:
                l.append(sample.split(','))

    for sample in l:
        f.write(str(sample).replace("[","").replace("]","\n"))
    
    f.close()

    r.extend([int(sample[1]) for sample in l])
    ir.extend([int(sample[2]) for sample in l])
    c = c + 1
    if c == 20:
        c = 0

        r = np.array(r)
        ir = np.array(ir)
        
        print("normal :", 110-25*R(r, ir)[0], "pre-calibrated :", 110-25*R(r, ir, [1,4])[0])

        r = []
        ir = []


    for i in range(3):
        y_vec[i] = np.append(y_vec[i][:-50],[int(sample[i+1]) for sample in l])
    
    line = live_plotter(x_vec,y_vec,line) #plot line

    for i in range(3):
        y_vec[i] = np.append(y_vec[i][50:],[0]*50) #delete 1st-25th data point

def on_message(client, userdata, message):
    if message.topic == "esp32/data":
        data(message)
    
broker_address = "127.0.0.1" 

client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback

client.connect(broker_address) #connect to broker
client.subscribe("esp32/data") #subscribe to topic



if __name__ == "__main__":
    ppg_setting()
    client.loop_start()
    esp_start_transmittion()
    sleep(10)
    esp_stop_transmittion()
    # plt.close('all')
    client.loop_stop()

