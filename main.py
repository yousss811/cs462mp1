from reciever_modules import *

def main(): 
    #Get inputs from file
    recieved_sig_vals = read_file_float('input.txt')

    #Down conversion
    f_c = 20
    T = 1/100
    num_samples = 3000

    #plotting dbg
    #init_plots()
    #plot_input_values = plot_signal_and_fft(recieved_sig_vals, num_samples, T)
    #done dbg

    I_down_converted = down_convert(recieved_sig_vals, f_c, T, num_samples, 'cos')

    Q_down_converted = down_convert(recieved_sig_vals, f_c, T, num_samples, 'sin')

    #plotting dbg
    #plot_I_down_converted = plot_signal_and_fft(I_down_converted, num_samples, T)
    #plot_Q_down_converted = plot_signal_and_fft(Q_down_converted, num_samples, T)
    #done dbg

    #Low pass filter
    f_cutoff = 5.1
    f_s = 100
    order = 1

    """
    lpf = create_lpf(f_cutoff, f_s, order)
    I_filtered = apply_lpf(I_down_converted, lpf)
    Q_filtered = apply_lpf(Q_down_converted, lpf)
    """
    I_dc_fft = fft(I_down_converted)
    Q_dc_fft = fft(Q_down_converted) 

    I_filtered_fft = zero_out(I_dc_fft, f_cutoff, f_s, num_samples, T)
    Q_filtered_fft = zero_out(Q_dc_fft, f_cutoff, f_s, num_samples, T)

    I_filtered = ifft(I_filtered_fft)
    Q_filtered = ifft(Q_filtered_fft)
    
    #multiply by two since amplitude is halved after filtration
    #for i in range(len(I_filtered)): 
        #I_filtered[i] *= 2
        #Q_filtered[i] *= 2
        
        

    #plotting dbg
    #plot_I_filtered = plot_signal_and_fft(I_filtered, num_samples, T)
    #plot_Q_filtered = plot_signal_and_fft(Q_filtered, num_samples, T)
    #done dbg

    #Downsample
    sym_transmission_freq = 10

    I_downsampled = downsample(I_filtered, sym_transmission_freq)

    Q_downsampled = downsample(Q_filtered, sym_transmission_freq)

    #plotting dbg
    #plot_I_down_sampled = plot_signal_and_fft(I_downsampled, int(num_samples/10), T*10)
    #plot_Q_down_sampled = plot_signal_and_fft(Q_downsampled, int(num_samples/10), T*10)
    #show_plots()
    #done dbg

    #Correlate 
    n = 251
    start_index = correlate(I_downsampled, Q_downsampled, 'preamble.txt', n)
    if start_index == 0: 
        print("Error: not correlated properly, preamble not found")
        #return -1

    #Extract bits from singals
    num_samples = 300 - start_index 
    bits = demodulate(I_downsampled, Q_downsampled, num_samples, start_index)

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