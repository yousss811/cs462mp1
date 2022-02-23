import numpy as np
from matplotlib import pyplot as plt

#Create I and Q input lists
input = open('input.txt', 'r')
input_values = input.readlines()
Iinput = []
Qinput = []
for string_value in input_values: 
    Iinput.append(float(string_value.strip()))
    Qinput.append(0)

#Create I and Q preamble lists
preamble = open('preamble.txt', 'r')
preamble_values = preamble.readlines()
preamble_values = np.array(preamble_values)
preamble_values = np.char.replace(preamble_values, 'i', 'j').astype(np.complex128)
Ipreamble = []
Qpreamble = []
for complex_value in preamble_values: 
    Ipreamble.append(complex_value.real)
    Qpreamble.append(complex_value.imag)


#x = np.arange(3000)
#y = values
#plt.title("Input Values")
#plt.xlabel("sample num")
#plt.ylabel("input value")
#plt.plot(x,y)
#plt.show()