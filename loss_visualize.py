from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

data = open("data.txt","r").read().replace("'","").split("\n")
samples = [sample.split(", ") for sample in data][:-1]

STE = (datetime.strptime(samples[-1][0], '%d/%m/%Y %H:%M:%S.%f') - \
        datetime.strptime(samples[0][0], '%d/%m/%Y %H:%M:%S.%f'))

print(STE.seconds + STE.microseconds/1000000,len(samples)/250)

interval = []
last = datetime.strptime(samples[0][0], '%d/%m/%Y %H:%M:%S.%f')
for sample in samples:
    t = datetime.strptime(sample[0], '%d/%m/%Y %H:%M:%S.%f')
    interval.append((t-last).microseconds)
    last = t

interval_np = np.around(np.array(interval)/4000)

loss = np.sum(interval)/4000 - len(interval)
print(loss*4/1000 + 4)

plt.plot(interval)
plt.show()
