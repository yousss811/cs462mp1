import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft, ifft, fftfreq 
from scipy.signal import butter, lfilter

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

#!!!  NOT USED !!!
#Zero out all values not in frequency range +/- f_cuttoff in fft graph
#Input: fft of signal as float array
#Output: filtered fft of signal as float array
def zero_out(signal_array, f_c, f_s, num_samples, T): 
    frequencies = fftfreq(num_samples, T)
    signal_array_filtered = []
    for i in range(num_samples): 


        if i<(num_samples/2): 
            curr_freq = f_s * frequencies[i]
        else: 
            curr_freq = f_s * (i - num_samples)


        if abs(curr_freq) < f_c : 
            signal_array_filtered.append(0)
        else: 
            signal_array_filtered.append(signal_array[i])
    return signal_array_filtered


        

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
#Output: index of the last byte of the preamble else if no match -1
def correlate(I_signal_array, Q_signal_array, preamble, n): 
    preamble_array = read_file_str(preamble)
    start_index = 0
    restart_index = 0
    preamble_index = 0
    i = 0
    while i < n: 
        #create string of complex num using I and Q
        if Q_signal_array[i] < 0: 
            IQstr = '{}{}i'.format(five_sig_figs(I_signal_array[i]), five_sig_figs(Q_signal_array[i]))
        else: 
            IQstr = '{}+{}i'.format(five_sig_figs(I_signal_array[i]), five_sig_figs(Q_signal_array[i]))

        if .48283 < five_sig_figs(I_signal_array[i]) < .48285: 
            print("OK Working")
        if IQstr == preamble_array[preamble_index]: 
            preamble_index +=1
            if preamble_index == 1: 
                restart_index = i
            if preamble_index == 50: 
                start_index = i 
                break
        elif preamble_index > 0: 
            preamble_index = 0
            i = restart_index
        i += 1


        

        """
        if Q_signal_array[i] < 0: 
            IQstr = '{}{}i'.format(five_sig_figs(I_signal_array[i], Q_signal_array[i]))
        else: 
            IQstr = '{}+{}i'.format(five_sig_figs(I_signal_array[i]), five_sig_figs(Q_signal_array[i]))
        if IQstr != preamble_array[i]: 
            return False
        """
    return start_index

#Demodulate: assign bit values based off signal values (QAM16)     
#Input: I and Q as float arrays, int num_samples
#Output: string array of bits, each element has 8 bits
def demodulate(I_signal_array, Q_signal_array, num_samples, start_index):
    cut_I_sig_arr = I_signal_array[start_index:]
    cut_Q_sig_arr = Q_signal_array[start_index:]
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
def init_plots():
    global curr_num_graphs
    curr_num_graphs = 0
def plot_signal_and_fft(signal_as_array, num_samples, T): 
    global curr_num_graphs
    curr_plt = plt.figure(curr_num_graphs+1)
    curr_num_graphs += 1
    plt.subplot(1,2,1)
    plt.plot(signal_as_array, 'r')
    plt.subplot(1,2,2)
    signal_fft = fft(signal_as_array)
    frequencies = fftfreq(num_samples, T)
    plt.plot(frequencies, signal_fft, 'b')
    return curr_plt
def show_plots(): 
    plt.show()



