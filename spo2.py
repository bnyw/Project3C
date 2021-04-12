import numpy as np
from scipy.signal import find_peaks, peak_prominences
import matplotlib.pyplot as plt
from numpy.fft import fft, ifft
from arr import mutual, between

FILENAME = "data.txt"
DIST = 120
PROM = 120
START, END = 2200, 2600
REDMUL, IRMUL = 1,4

def peaks(input_signal, btw = False):
    pp, _ = find_peaks(input_signal, distance=DIST, prominence=PROM)
    np, _ = find_peaks(-input_signal, distance=DIST, prominence=PROM)

    if btw:
        return between(pp,np)
    return (pp, np)

def R(red, ir, AC_multiplier = [1,1]):
    rPeak, rValley = peaks(red, btw = True)
    irPeak, irValley = peaks(ir, btw = True)
    
    rPeak, irPeak = mutual(rPeak,irPeak)
    rValley, irValley = mutual(rValley,irValley)

    rAC = red[rPeak] - red[rValley]
    irAC = ir[irPeak] - ir[irValley]

    nume = (rAC/irAC)*(AC_multiplier[0]/AC_multiplier[1])
    denom = (ir[irPeak] - irAC/2)/(red[rPeak] - rAC/2)

    R = np.mean(nume/denom)

    pos_peaks = [rPeak, irPeak]
    neg_peaks = [rValley, irValley]

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
    axes[1].plot(hat_pos[0], redC[hat_pos[0]], "x")
    axes[1].plot(hat_neg[0], redC[hat_neg[0]], "x")

    axes[1].plot(irC, c = "black", label = "IR^")
    axes[1].plot(hat_pos[1], irC[hat_pos[1]], "x")
    axes[1].plot(hat_neg[1], irC[hat_neg[1]], "x")

    plt.show()
