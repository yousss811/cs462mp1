import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft, ifft, fftfreq
from scipy.signal import firwin, freqz, butter, lfilter


#read input values into list
input = open('input.txt', 'r')
input_values = input.readlines()

preamble = open('preamble.txt', 'r')
preamble_values = preamble.readlines()


#--------------#
#down conversion
#
#input_values = d(t) = I(t)cos(2*pi*f*t) + Q(t)sin(2*pi*f*t)
#
#multiply input values by cos(2*pi*f*t) and sin(2*pi*f*t) respectively
#
#I = I(t)/2  +  Q(t)sin(4*pi*f*t)+ I(t)cos(4*pi*f*t) / 2
#Q = Q(t)/2  +  Q(t)sin(4*pi*f*t)+ I(t)cos(4*pi*f*t) / 2
#
#--------------#
f = 20
T = 1/100
num_samples = 3000
#create 3000 sample long cos(2*pi*f*n*T) list
cos_input = np.cos([2*np.pi*f*n*T for n in range(num_samples)])
#create 3000 sample long sin(2*pi*f*n*T) list
sin_input = np.sin([2*np.pi*f*n*T for n in range(num_samples)])

#multiply input by cos and sin for I and Q respectively
I = [float(input_values[i])*cos_input[i] for i in range(num_samples)]
Q = [float(input_values[i])*sin_input[i] for i in range(num_samples)]

#plot I, Q and their fft graphs
I_fft = fft(I)
Q_fft = fft(Q)
frequencies = fftfreq(num_samples, T)

IandQwithFFTs = plt.figure(1)
plt.subplot(2,2,1)
plt.title("I")
plt.plot(I)
plt.subplot(2,2,2)
plt.title("I fft")
plt.plot(frequencies, I_fft)
plt.subplot(2,2,3)
plt.title("Q")
plt.plot(Q)
plt.subplot(2,2,4)
plt.title("Q fft")
plt.plot(frequencies, Q_fft)
#plt.show()



#--------------#
#low pass filter
#
# I = I(t)/2  +  (Q(t)sin(4*pi*f*t)+ I(t)cos(4*pi*f*t) / 2)
# Q = Q(t)/2  +  (Q(t)sin(4*pi*f*t)+ I(t)cos(4*pi*f*t) / 2)
#                                ^
#                        lpf removes this term
#
# I_filtered = I(t)/2
# Q_filtered = Q(t)/2
#
#--------------#
f1 = 5.1
fs = 100
f_nyq = .5 * fs
order = 1

#create lpf
norm_cuttoff_freq = (2 * f1)/fs
lpf_numerator, lpf_denominator = butter(order, norm_cuttoff_freq)


#apply lpf on our signals I and Q
I_filtered = lfilter(lpf_numerator, lpf_denominator, I) #ifft([I_fft[i] * lpf[i] for i in range(num_samples)])
Q_filtered = lfilter(lpf_numerator, lpf_denominator, Q) #ifft([Q_fft[i] * lpf[i] for i in range(num_samples)])

#plot filtered I and Q
IandQFILTEREDwithFFTs = plt.figure(2)
plt.subplot(2,2,1)
plt.title("I filtered")
plt.plot(I_filtered)
plt.subplot(2,2,2)
plt.title("I fft filtered")
plt.plot(frequencies, fft(I_filtered))
plt.subplot(2,2,3)
plt.title("Q filtered")
plt.plot(Q_filtered)
plt.subplot(2,2,4)
plt.title("Q fft filtered")
plt.plot(frequencies, fft(Q_filtered))
plt.show()


#--------------#
#downsample
#
# Take only every 10th sample to make the new f_s = 10Hz
#
#--------------#
#take every 10th sample - total sample size is now 300, f_s = 10Hz
I_downsamp = [I_filtered[i] for i in range(num_samples) if i%10 == 0]
Q_downsamp = [Q_filtered[i] for i in range(num_samples) if i%10 == 0]



#--------------#
#correlate
#--------------#
#small helper function to round to 5 sig figs
def five_sig_figs(x, sig = 5):
    if x == 0: 
        return 0
    return round(float(x), sig-int(np.floor(np.log10(np.abs(x))))-1)
#check first 50 samples vs preamble
for i in range(50):
    IQstr = "{}-{}i".format(five_sig_figs(I_downsamp[i]), five_sig_figs(Q_downsamp[i]))
    print(IQstr, preamble_values[i])
    if IQstr != preamble_values[i]: 
        print("Preamble and Current Signal do not match")
        break



#--------------#
#demodulate
#
# based on the values of I and Q at a specific point of time, assign the proper bit code as seen in QAM16
#
#--------------#
#bits will be returned here as strings in groups of 4
bits = []

for i in range(300):
    bit1 = -1
    bit2 = -1
    bit3 = -1
    bit4 = -1
    bit_segment = ""   
    #if Q is positive then bit 1 is 0, otherwise bit 1 is 1
    if Q[i] > 0: 
        bit1 = 0
    else:
        bit1 = 1
    #if abs(Q) is greater than 2 bit 2 is 1, otherwise bit 2 is 0
    if np.abs(Q[i]) < 2: 
        bit2 = 1
    else: 
        bit2 = 0
    #if Q is positive then bit 3 is 0, otherwise bit 3 is 1
    if I[i] > 0:
        bit3 = 0
    else: 
        bit3 = 1
    #if abs(I) is greater than 2 bit 4 is 1, otherwise bit 4 is 0
    if np.abs(I[i]) < 2: 
        bit4 = 1
    else: 
        bit4 = 0

    bit_segment = "{}{}{}{}".format(bit1, bit2, bit3, bit4)
    bits.append(bit_segment)



#--------------#
#Ascii to text
#
# group bits by 8 and translate into ascii code 
#
#--------------#
bits_grouped_by_8 = [bits[i]+bits[i+1] for i in range(len(bits) - 1) if i%2 == 0]
ascii_text = ''
for i in range(len(bits_grouped_by_8)):
    print(chr(int(bits_grouped_by_8[i])))
    ascii_text += chr(int(bits_grouped_by_8[i]))





#--------------#
#some plotting things for debugging
#--------------#

#plot1 = plt.figure(1)
#plt.plot(cos_input)
#plt.plot(sin_input)

#plot2 = plt.figure(2)
#plt.subplot(2,2,1)
#plt.plot(I, 'r')
#plt.subplot(2,2,2)
#plt.plot(fft(I), 'b')
#plt.subplot(2,2,3)
#w1, h1 = freqz(I)
#plt.plot(w1, 20*np.log10(np.abs(h1)), 'g')
#
#plot3 = plt.figure(3)
#plt.subplot(2,2,1)
#plt.plot(Q, 'r')
#plt.subplot(2,2,2)
#plt.plot(fft(Q), 'b')
#plt.subplot(2,2,3)
#w2, h2 = freqz(Q)
#plt.plot(w2, 20*np.log10(np.abs(h2)), 'g')
#
#plot4 = plt.figure(4)
#init_vals = [float(input_values[i]) for i in range(num_samples)]
#plt.subplot(2,2,1)
#plt.plot(init_vals, 'r')
#plt.subplot(2,2,2)
#plt.plot(fft(init_vals), 'b')
#plt.subplot(2,2,3)
#w3, h3 = freqz(init_vals)
#plt.plot(w3, 20*np.log10(np.abs(h3)), 'g')
#
#plt.show()
#

















