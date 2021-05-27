import sys
import os

import paho.mqtt.client as mqtt

from PySide6 import QtWidgets, QtGui, QtCore
from ui import Ui_MainWindow
from pyqtgraph.ptime import time

from spo2 import R, SPO2, HeartRate

import json
import numpy as np

class ESM(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # Connection
        self.broker_address = "127.0.0.1" 
        self.client  = mqtt.Client("P1") 
        self.client.on_message = self.on_message

        # Save's signaling
        self.browse.clicked.connect(self.browse_file)
        self.setSaveState.clicked.connect(self.set_save_state)
        self.save_state = False
        self.pauseSave.clicked.connect(self.pause_save)
        self.pause_state = False

        # Setting's signaling
        self.setSetting.clicked.connect(self.ppg_setting)

        # Plot's signaling & setting
        self.setNsample.clicked.connect(self.esp_set_Nsample)
        self.setPlotSize.clicked.connect(self.set_plot_size)
        self.plot_size = 1000
        self.setPlotState.clicked.connect(self.set_plot_state)
        self.plot_state = False

        self.ppg.setRange(QtCore.QRectF(0, 0, self.plot_size, 80000)) 
        self.ppg.enableAutoRange()

        self.redLine = self.ppg.plot(pen='r')
        self.irLine = self.ppg.plot(pen='w')

        self.ecgLine = self.ecg.plot(pen='g')
        self.ecg.setRange(QtCore.QRectF(0, 0, self.plot_size, 4096)) 
        self.ecg.enableAutoRange()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)

        self.lastTime = time()
        self.fps = None
        self.R_list = []
        self.HR_list = []

        self.timestamp_data, self.red_data, self.ir_data, self.ecg_data = [], [], [], []

        # Advance
        self.timer2 = QtCore.QTimer()
        self.timer2.timeout.connect(self.check_esp_status)
        # self.timer2.start(10000)

    def open(self):
        self.client.connect(self.broker_address)
        self.client.subscribe("esp32/data")
        self.client.subscribe("esp32/status")
        self.client.loop_start()
        self.set_esp_transmission_state(1)

    def close(self):
        self.set_esp_transmission_state(0)
        self.client.loop_stop()
        self.client.disconnect()

    def ppg_setting(self):
        """
        led     : "ledBrightness" :   Options: 0=Off to 255=50mA \n
        savg    : "sampleAverage" :   Options: 1, 2, 4, 8, 16, 32 \n
        mode    : "ledMode"       :   Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green \n
        sr      : "sampleRate"    :   Options: 50, 100, 200, 400, 800, 1000, 1600, 3200 \n
        pw      : "pulseWidth"    :   Options: 69, 118, 215, 411 \n
        adc     : "adcRange"      :   Options: 2048, 4096, 8192, 16384 \n
        """
        setting_dict = {
            "ledBrightness" : self.ledBrightness.value(),
            "sampleAverage" : self.sampleAverage.currentText(),
            "ledMode" : self.ledMode.currentIndex()+1,
            "sampleRate" : self.sampleRate.currentText(),
            "pulseWidth" : self.pulseWidth.currentText(),
            "adcRange" : self.adcRange.currentText()
        }
        setting_json = json.dumps(setting_dict)
        self.client.publish("esp32/max30102_setting", setting_json)

    def esp_set_Nsample(self):
        self.client.publish("esp32/Nsampling", self.Nsample.value())

    def set_esp_transmission_state(self, state):
        self.client.publish("esp32/transmission_state", state)

    def check_esp_status(self):
        self.client.publish("esp32/check_status", "some text")

    def trimData(self, Nleft):
        if len(self.red_data) > Nleft:
            self.red_data[:-Nleft] = []
            self.ir_data[:-Nleft] = []
            self.ecg_data[:-Nleft] = []
            self.timestamp_data[:-Nleft] = []

    def data(self, message):
        samples = str(message.payload.decode("utf-8")).split('END')[0].split('#')

        # f = open(fname,'a+')
        l = []
        for sample in samples:
            if len(sample) != 0:
                l.append(sample.split(','))
                if self.save_state == True:
                    self.f.write(str(l[-1]).replace("[","").replace("]","\n"))
        # f.close()

        for sample in l:
            self.timestamp_data.extend([sample[0]])
            self.red_data.extend([int(sample[1])])
            self.ir_data.extend([int(sample[2])])
            self.ecg_data.extend([int(sample[3])])

    def on_message(self, client, userdata, message):
        if message.topic == "esp32/data":
            self.data(message)
        elif message.topic == "esp32/status":
            self.boardStatus.setText(str(message.payload.decode("utf-8")))

    def update(self):
        self.trimData(self.plot_size)

        self.redLine.setData(np.array(self.red_data))
        self.irLine.setData(np.array(self.ir_data))
        self.ecgLine.setData(np.array(self.ecg_data))

        self.now = time()
        dt = self.now - self.lastTime
        self.lastTime = self.now

        if self.fps is None:
            self.fps = 1.0/dt
        else:
            s = np.clip(dt*3., 0, 1)
            self.fps = self.fps * (1-s) + (1.0/dt) * s

        R_value, posPeak, negPeak = R(np.array(self.red_data), np.array(self.ir_data))
        
        if isinstance(R_value, float):
            self.R_list.append(R_value)
            HR = HeartRate(posPeak, self.timestamp_data)
            if HR != -1:
                self.HR_list.append(HR)

            if len(self.R_list) > 400:
                self.R_list[:-400] = []

            if len(self.HR_list) > 400:
                self.HR_list[:-400] = []

            self.ppg.setTitle('%0.2f fps, SpO2: %0.2f, SpO2^: %0.2f' % (self.fps, SPO2(np.mean(self.R_list)), SPO2(np.mean(self.R_list)/3.43)))
            self.ecg.setTitle('HeartRate: %d bpm' % (int(np.mean(self.HR_list))))

    def set_plot_size(self):
        self.plot_size = int(self.plotSize.value())

    def set_plot_state(self):
        self.plot_state = not self.plot_state
        if self.plot_state:
            self.setPlotState.setText("Stop plotting")
            self.timer.start(0)
        else:
            self.setPlotState.setText("Start plotting")
            self.timer.stop()

    def browse_file(self):
        fname = str(QtGui.QFileDialog.getSaveFileName()[0])
        if fname == '':
            path = os.path.expanduser("~/Documents/KMITL/EPM/")
            if not os.path.exists(path):
                os.makedirs(path)
            fname = "default_filename.txt"
            self.path.setText(path+fname)

        elif fname.endswith(".txt"):
            self.path.setText(fname)
        else:
            self.path.setText(fname+".txt")

    def set_save_state(self):
        self.save_state = not self.save_state
        if self.save_state:
            self.setSaveState.setText("Stop")
            self.pauseSave.setEnabled(True)
        else:
            self.setSaveState.setText("Start")
            self.pauseSave.setDisabled(True)
            self.pauseSave.setText("Pause")
            self.pause_state = False

    def pause_save(self):
        self.pause_state = not self.pause_state
        if self.pause_state:
            self.pauseSave.setText("Resume")
        else:
            self.pauseSave.setText("Pause")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ESM()
    window.open()
    window.show()
    app.exec_()
    window.close()
