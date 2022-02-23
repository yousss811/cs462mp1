from reciever_modules import *

def main(): 
    recieved_sig_vals = read_file_float('input.txt')

    #Down conversion
    f_c = 20
    T = 1/100
    num_samples = 3000

    #plotting dbg
    plot_signal_and_fft(recieved_sig_vals, num_samples, T)
    #done dbg

    I_down_converted = down_convert(recieved_sig_vals, f_c, T, num_samples, 'cos')

    Q_down_converted = down_convert(recieved_sig_vals, f_c, T, num_samples, 'sin')

    #plotting dbg
    plot_signal_and_fft(I_down_converted, num_samples, T)
    plot_signal_and_fft(Q_down_converted, num_samples, T)
    #done dbg

    #Low pass filter
    f_cutoff = 5.1
    f_s = 100
    order = 1

    lpf = create_lpf(f_cutoff, f_s, order)

    I_filtered = apply_lpf(I_down_converted, lpf)
    Q_filtered = apply_lpf(Q_down_converted, lpf)

    #plotting dbg
    plot_signal_and_fft(I_filtered, num_samples, T)
    plot_signal_and_fft(Q_filtered, num_samples, T)
    #done dbg

    #Downsample
    sym_transmission_freq = 10

    I_downsampled = downsample(I_filtered, sym_transmission_freq)

    Q_downsampled = downsample(Q_filtered, sym_transmission_freq)

    #plotting dbg
    plot_signal_and_fft(I_downsampled, int(num_samples/10), T*10)
    plot_signal_and_fft(Q_downsampled, int(num_samples/10), T*10)
    #done dbg

    #Correlate 
    n = 50
    if not correlate(I_downsampled, Q_downsampled, 'preamble.txt', n): 
        print("Error: not correlated properly")
        #return -1

    #Extract bits from singals
    num_samples = 300
    bits = demodulate(I_downsampled, Q_downsampled, num_samples)

    #Translate bits to ascii
    rtn_txt = 'NOT THE TEXT'
    if ascii_to_text(bits): 
        rtn_txt = ascii_to_text(bits)
    else: 
        print("Error: bits not correctly demodulated (not an ascii val)")
        #return -1

    print(rtn_txt)
    return rtn_txt


if __name__ == '__main__': 
    main()