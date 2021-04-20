import numpy as np
from numpy.core.numeric import Inf

def mutual(arr_a, arr_b):
    min = Inf
    swab = False

    # arr_a always contain more child
    if arr_a.shape[0] < arr_b.shape[0]:
        arr_a, arr_b = arr_b, arr_a
        swab = True

    la = []
    lb = []

    for i in range(len(arr_a)+len(arr_b)-1):
        if i < len(arr_a):
            la.append(i)
            lb.append(len(arr_b)-i-1)
            if len(la) == len(arr_b)+1:
                la.pop(0)
                lb.pop()
        else:
            la.pop(0)
            lb.pop(0)

        a = arr_a[np.array(la)]
        b = arr_b[np.array(lb[::-1])]

        dif = abs(a-b)
        if np.mean(dif) <= min:
            if swab:
                temp = (b, a)
            temp = (a, b)
    
    return temp
    # raise ValueError(a,b)

def between(peak, valley):
    """
    peak should not have an unexpected value
    """
    i = 0
    k = 0

    la = []
    lb = []

    lastPair = False
    # check if last value of valley is more than last value of peak
    try:
        if valley[-1] > peak[-1]:
            # if yes store it value and delete from arr
            lastPair = True
            temp = valley[-1]
            valley = np.delete(valley, -1)
    except IndexError:
        print(valley, peak)


    while i < len(valley)-k:
        if valley[i+k] >= peak[i] and valley[i+k] < peak[i+1]:
            la.append(peak[i])
            lb.append(valley[i+k])
            i = i + 1
        else:
            k = k + 1

    if lastPair:
        la.append(peak[i])
        lb.append(temp)
    
    return np.array(la), np.array(lb)

if __name__ == "__main__":
    a = np.array([26,177,342,488,638] )
    b = np.array([178,341,485,624])

    print(mutual(a,b))
