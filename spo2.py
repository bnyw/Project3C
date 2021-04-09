import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from numpy.fft import fft, ifft

FILENAME = "data_asia.txt"
DIST = 100
START, END = 1750, 2000
REDMUL, IRMUL = 1,4

def I(input_signal):
    global DIST
    pos_peaks, _ = find_peaks(input_signal, distance=DIST)
    neg_peaks, _ = find_peaks(-input_signal, distance=DIST)

    length = min(len(pos_peaks),len(neg_peaks))
    AC = (input_signal[pos_peaks][:length] - input_signal[neg_peaks][:length])
    DC = input_signal[pos_peaks][:length] - AC/2
    try:
        I = np.mean(AC/DC)
    except RuntimeWarning:
        print("Except",AC)
    return I, pos_peaks, neg_peaks

def R(red, ir, AC_multiplier = [1,1]):
    red_I, red_pos_peaks, red_neg_peaks = I(red)
    ir_I, ir_pos_peaks, ir_neg_peaks = I(ir)

    R = (red_I*AC_multiplier[0])/(ir_I*AC_multiplier[1])
    pos_peaks = [red_pos_peaks, ir_pos_peaks]
    neg_peaks = [red_neg_peaks, ir_neg_peaks]

    return R, pos_peaks, neg_peaks

def Calibrated(input_signal, mul):
    ft = fft(input_signal)
    ft[1:] = ft[1:]*mul
    return ifft(ft).real

if __name__ == "__main__":
    data = open(FILENAME,"r").read().replace("'","").split("\n")
    samples = [sample.split(", ") for sample in data][:-1]

    red, ir = [], []
    for sample in samples:
        red.append(int(sample[1]))
        ir.append(int(sample[2]))

    # RED
    red = np.array(red[START:END])

    # INFRARED
    ir = np.array(ir[START:END])

    R1, norm_pos, norm_neg = R(red, ir)
    R2, hat_pos, hat_neg = R(red, ir, [REDMUL,IRMUL])

    print("R", R1,"R^", R2)
    print('SpO2 =', 110-(25*R1), 'SpO2^ =', 110-(25*R2))

    redC = Calibrated(red, REDMUL)
    irC = Calibrated(ir, IRMUL)

    fig, axes = plt.subplots(1, 2)

    axes[0].plot(red, c = "red", label = "RED")
    axes[0].plot(norm_pos[0], red[norm_pos[0]], "x")
    axes[0].plot(norm_neg[0], red[norm_neg[0]], "x")

    axes[0].plot(ir, c = "black", label = "IR")
    axes[0].plot(norm_pos[1], ir[norm_pos[1]], "x")
    axes[0].plot(norm_neg[1], ir[norm_neg[1]], "x")


    axes[1].plot(redC, c = "red", label = "RED^")
    axes[1].plot(norm_pos[0], redC[norm_pos[0]], "x")
    axes[1].plot(norm_neg[0], redC[norm_neg[0]], "x")

    axes[1].plot(irC, c = "black", label = "IR^")
    axes[1].plot(norm_pos[1], irC[norm_pos[1]], "x")
    axes[1].plot(norm_neg[1], irC[norm_neg[1]], "x")

    plt.show()
