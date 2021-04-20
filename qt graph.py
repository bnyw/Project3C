from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
from spo2 import read_from_file

app = pg.mkQApp("Plot Speed Test")
red, ir = (np.array(x) for x in read_from_file())

p = pg.plot()
p.setWindowTitle('pyqtgraph example: PlotSpeedTest')
p.setRange(QtCore.QRectF(0, 0, 500, max(red))) 
p.setLabel('bottom', 'Index', units='B')

curve1 = p.plot(pen='r')
curve2 = p.plot(pen='w')

ptr = 0
lastTime = time()
fps = None
def update():
    global curve1, red, ir, ptr, p, lastTime, fps
    if ptr+500 == len(red):
        ptr = 0
    curve1.setData(red[ptr:ptr+500])
    curve2.setData(ir[ptr:ptr+500])
    ptr += 1
    now = time()
    dt = now - lastTime
    lastTime = now
    if fps is None:
        fps = 1.0/dt
    else:
        s = np.clip(dt*3., 0, 1)
        fps = fps * (1-s) + (1.0/dt) * s
    p.setTitle('%0.2f fps' % fps)
    app.processEvents()  ## force complete redraw for every plot
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)
    
if __name__ == '__main__':
    pg.mkQApp().exec_()