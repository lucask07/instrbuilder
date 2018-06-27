# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import scipy.signal as signal
import numpy as np
import matplotlib.pyplot as plt

order = 3
sample_rate = 780 # Hz 
tau = 500e-3 
cutoff_freq = 1/(2*np.pi*tau)
norm_cutoff_freq = cutoff_freq/(sample_rate/2) # [from 0 - 1]

b,a = signal.iirfilter(N = order, Wn = norm_cutoff_freq, 
	rp=None, rs=None, btype='lowpass', analog=False, 
	ftype='butter', output='ba')

w, h = signal.freqz(b, a, 10000)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.semilogx(w, 20 * np.log10(abs(h*(1))), marker = 'x')

plt.figure()
plt.plot(arr, marker = 'x')
# timeit: 107 us with array of 1024
output_signal = signal.filtfilt(b, a, arr)
plt.plot(output_signal, marker = 'o')

# timeit: 142 us with array of 4096
# l = np.concatenate((arr,arr,arr,arr))
# output_signal = signal.filtfilt(b, a, l)

print('Total data time = {} [s]'.format(len(arr)*1/sample_rate))
print('Total data time = {} [Tau]'.format(len(arr)*1/sample_rate/tau))

# Three options:
# 1) perfectly frequency locked, DC signal, relative phase does not change 
#	DC amplitude depends on phase, could search for optimum phase
# 2) frequency difference less than LPF cutoff. (similar to 1 above with f = 0)
#	Will get a Q result that oscillates with time 
# 3) frequency difference greater than LPF cutoff
#	Will get a Q result attenuated by the filter 
# ---- 
# does toggling between I and Q help? Maybe if the switching is at a rate, much-much less than the freq difference
# Need DMM signal that indicates when triggering is complete (toggling operation around ~20 ms or greater) 
# OPC? 

# Example 3000 Hz Mixer clock, 2999 Hz signal, sampled at 24kHz  
# phase drifts at 1 Hz 
# time-constant of 30 ms (fc = 5.3 Hz)

# 12.24 degrees (wrpt 1 Hz) in 1024*1/30e3 = 0.0341 s

# ==> I should force a large time-constant so that this isn't much of an issue 
