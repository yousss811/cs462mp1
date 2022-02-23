import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft 
from scipy.signal import butter, lfilter, freqz

#Reads every line in the file and returns each line as an element in an array 
#Input: file name as string
#Output: float array with each line of file as an element
def read_file_float(file): 
    file = open(file, 'r')
    return np.array(file.readlines(), float)

#Similar to above, but returns as string array
def read_file_str(file): 
    file = open(file, 'r')
    return np.array(file.readlines(), str)
   
#Return signal to baseband 
#Input: sampled signal as float array, center frequency in Hz, number of samples, and the function to be used (in this case only 'cos' or 'sin')
#Output: A float array after down conversion by specified function
def down_convert(signal_array, f_c, T, num_samples, convert_func_str): 
    #create an appropriate sized array for conversion function 
    if convert_func_str.lower() == 'cos': 
        convert_func_array = np.array(np.cos([2*np.pi*f_c*T*n for n in range(num_samples)]), float)
    if convert_func_str.lower() == 'sin':  
        convert_func_array = np.array(np.sin([2*np.pi*f_c*T*n for n in range(num_samples)]), float)
    
    return np.array([signal_array[i]*convert_func_array[i] for i in range(num_samples)], float)

#Create low pass filter with parameters
#Input: cutoff freq, sampling freq, order of filter
#Output: array of tuples with tuple[0] is numerator and tuple[1] is denominator of filter
def create_lpf(f_cutoff, f_s, order):
    f_nyq = .5*f_s
    norm_cuttoff_freq = (2 * f_cutoff) / f_s

    lpf_numerator, lpf_denominator = butter(order, norm_cuttoff_freq)
    lpf = [[lpf_numerator[i], lpf_denominator[i]] for i in range(max(len(lpf_numerator), len(lpf_denominator)))]
    return lpf

#Apply lpf on signal
#Input: signal, lpf as outputted by create_lpf 
#Output: Filtered signal as float array
def apply_lpf(signal_array, lpf): 
    lpf_numerator = [lpf[i][0] for i in range(len(lpf))]
    lpf_denominator = [lpf[i][1] for i in range(len(lpf))]
    return lfilter(lpf_numerator, lpf_denominator, signal_array)

#Downsample a signal to symbol transmission frequency
#Input: symbol transmission freq in Hz as int, signal as float array
#Output: downsampled signal as float array 
def downsample(signal_array, sym_transmission_freq):
    return [signal_array[i] for i in range(len(signal_array)) if i%sym_transmission_freq == 0]

#small helper function to round to 5 sig figs
def five_sig_figs(x, sig = 5):
    if x == 0: 
        return 0
    new_sig = int(sig - int(np.floor(np.log10(np.abs(x)))) - 1)
    x = float(x)
    rtn_val = round(x, new_sig)
    return rtn_val

#Correlate: check first n samples vs provided pre-amble
#Input: I and Q signals as float arrays, pre-amble as string array, int num samples to check
#Output: bool - true if matching else false
def correlate(I_signal_array, Q_signal_array, preamble, n): 
    preamble_array = read_file_str(preamble)
    for i in range(n-1): 
        if Q_signal_array[i] < 0: 
            IQstr = '{}{}i'.format(five_sig_figs(I_signal_array[i], Q_signal_array[i]))
        else: 
            IQstr = '{}+{}i'.format(five_sig_figs(I_signal_array[i]), five_sig_figs(Q_signal_array[i]))
        if IQstr != preamble_array[i]: 
            return False
    return True

#Demodulate: assign bit values based off signal values (QAM16)     
#Input: I and Q as float arrays, int num_samples
#Output: string array of bits, each element has 8 bits
def demodulate(I_signal_array, Q_signal_array, num_samples):
    bits = []
    for i in range(num_samples):
        bit1 = -1
        bit2 = -1
        bit3 = -1
        bit4 = -1
        bit_segment = ""   
        #if Q is positive then bit 1 is 0, otherwise bit 1 is 1
        if Q_signal_array[i] > 0: 
            bit1 = 0
        else:
            bit1 = 1
        #if abs(Q) is greater than 2 bit 2 is 1, otherwise bit 2 is 0
        if np.abs(Q_signal_array[i]) < 2: 
            bit2 = 1
        else: 
            bit2 = 0
        #if Q is positive then bit 3 is 0, otherwise bit 3 is 1
        if I_signal_array[i] > 0:
            bit3 = 0
        else: 
            bit3 = 1
        #if abs(I) is greater than 2 bit 4 is 1, otherwise bit 4 is 0
        if np.abs(I_signal_array[i]) < 2: 
            bit4 = 1
        else: 
            bit4 = 0
    
        bit_segment = "{}{}{}{}".format(bit1, bit2, bit3, bit4)
        bits.append(bit_segment)
    return [bits[i] + bits[i+1] for i in range(len(bits)-1) if i%2 == 0]

#Ascii to text
#Input: string array of bits grouped by 8
#Output: string of corresponding text
def ascii_to_text(bit_array):
    ascii_text = ''
    for i in range(len(bit_array)):
        if int(bit_array[i]) > 0b110000:
            return False
        ascii_text += chr(int(bit_array[i]))
    return ascii_text

#Plot a signal and its fft
def plot_signal_and_fft(signal_as_array): 
    plt.subplot(1,2,1)
    plt.plot(signal_as_array)
    plt.subplot(1,2,2)
    signal_fft = fft(signal_as_array)
    w, h = freqz(signal_fft)
    plt.plot(w, h)
    plt.show()





