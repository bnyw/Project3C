import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from numpy.fft import fft, ifft
from arr import between
from datetime import datetime

FILENAME = "data.txt"
DIST = 80
PROM = 100
START, END = 1900, 2900
REDMUL, IRMUL = 1,4

def peaks(input_signal):
    peak, _ = find_peaks(input_signal, distance=DIST, prominence=PROM)
    valley, _ = find_peaks(-input_signal, distance=DIST, prominence=PROM)

    if len(peak) == 0 or len(valley) == 0:
        return None, None
    # Use between function to ensure that peak&valley can pair up and there won't be any value left
    peak, valley = between(peak, valley)

    if len(peak) == 0 or len(valley) == 0:
        return None, None

    return peak, valley

def R(red, ir, AC_multiplier = [1,1]):
    rPeak, rValley = peaks(red)
    irPeak, irValley = peaks(ir)

    if isinstance(rPeak, np.ndarray) and isinstance(rValley, np.ndarray) and isinstance(irPeak, np.ndarray) and isinstance(irValley, np.ndarray):
        rAC = np.mean(red[rPeak]) - np.mean(red[rValley])
        irAC = np.mean(ir[irPeak]) - np.mean(ir[irValley])

        nume = (rAC/(np.mean(red[rPeak]) - rAC/2))*AC_multiplier[0]
        denom = (irAC/(np.mean(ir[irPeak]) - irAC/2))*AC_multiplier[1]

        R = nume/denom

        pos_peaks = [rPeak, irPeak]
        neg_peaks = [rValley, irValley]

        return R, pos_peaks, neg_peaks

    return None, None, None

def Calibrated(input_signal, mul):
    s = 5
    e = 500
    ft = fft(input_signal)
    ft[e:] = ft[e:]*0
    ft[s:e] = ft[s:e]*mul
    return ifft(ft).real

def SPO2(R):
    return 110-(25*R)

def HeartRate(pos, timestamp):
    rPeak, irPeak = pos

    if len(rPeak) <= 1:
        return -1

    t = []

    for location in rPeak:
        t.append(datetime.strptime(timestamp[location], '%d/%m/%Y %H:%M:%S.%f'))

    ds_list = []
    for i in range(len(t)-1):
        ds = t[i+1] - t[i]
        ds_list.append(ds.microseconds/1000000)

    return 60/np.mean(ds_list)

def read_from_file(fname):
    data = open(fname,"r").read().replace("'","").split("\n")
    samples = [sample.split(", ") for sample in data][:-1]

    red, ir = [], []
    for sample in samples:
        red.append(int(sample[1]))
        ir.append(int(sample[2]))

    return red, ir

if __name__ == "__main__":
    red, ir = read_from_file(FILENAME)

    red = np.array(red[START:END])
    ir = np.array(ir[START:END])

    redC = Calibrated(red, REDMUL)
    irC = Calibrated(ir, IRMUL)

    R1, norm_pos, norm_neg = R(red, ir)
    R2, hat_pos, hat_neg = R(redC, irC)

    print("R", R1,"R^", R2)
    print('SpO2 =', 110-(25*R1), 'SpO2^ =', 110-(25*R2))

    fig, axes = plt.subplots(1, 2)

    axes[0].plot(red, c = "red", label = "RED")
    axes[0].plot(norm_pos[0], red[norm_pos[0]], "x")
    axes[0].plot(norm_neg[0], red[norm_neg[0]], "x")

    axes[0].plot(ir, c = "black", label = "IR")
    axes[0].plot(norm_pos[1], ir[norm_pos[1]], "x")
    axes[0].plot(norm_neg[1], ir[norm_neg[1]], "x")

    axes[0].legend(loc='best')

    axes[1].plot(redC, c = "red", label = "RED^")
    axes[1].plot(hat_pos[0], redC[hat_pos[0]], "x")
    axes[1].plot(hat_neg[0], redC[hat_neg[0]], "x")

    axes[1].plot(irC, c = "black", label = "IR^")
    axes[1].plot(hat_pos[1], irC[hat_pos[1]], "x")
    axes[1].plot(hat_neg[1], irC[hat_neg[1]], "x")

    axes[1].legend(loc='best')

    plt.show()
