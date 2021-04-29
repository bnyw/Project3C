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

def between(peaks, valleys) -> list:
    """
    Retrive 2 array and construct 2 new array that it value are alternate between each pair of value
    \nsuch as [10 20 30 40] and [15 25 35 45] are output from [10 20 30 40], [15 16 17 18 25 35 36 45]
    \npeak shouldn't have an unexpected value and must occur in ascending order
    """
    i ,k = 0, 0

    la = []
    lb = []

    # lastPair = False

    # if len(valleys) >= len(peaks):
    # check if each value of valleys is more than last value of peaks
    # for j, valley in enumerate(valleys):
    #     if valley > peaks[-1]:
    #         # if yes store it value and delete the rest from array
    #         lastPair = True
    #         temp = valley
    #         valleys = np.delete(valleys, np.s_[-len(valleys)+j:])
    #         break

    try:
        while i < len(peaks) - 1 and i+k <= len(valleys) - 1:
            # if k == len(valleys)-i:
            #     k = 1
            #     i += 1
            # print(i,k)
            if valleys[i+k] >= peaks[i] and valleys[i+k] < peaks[i+1]:
                la.append(peaks[i])
                lb.append(valleys[i+k])
                i += 1
            else:
                k += 1
            
            if k == len(valleys)-i:
                k = 1
                i += 1

            # print(la,lb)
    except Exception as e:
        print(e,i,k,peaks,valleys)
        # raise IndexError

    # try:
    #     if lastPair:
    #         la.append(peaks[i])
    #         lb.append(temp)
    # except Exception as e:
    #     print(e,i,k,peaks,valleys,la,lb)
    
    return np.array(la), np.array(lb)

if __name__ == "__main__":
    a = np.array([70, 234, 340, 461, 547, 648, 743])
    b = np.array([99, 184, 288, 412, 508, 608, 802, 902])

    print(between(a,b))
