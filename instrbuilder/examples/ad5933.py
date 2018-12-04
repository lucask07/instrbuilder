# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

from command import Register
from ic import IC
from ic import AA  # aardvark adapter

print('Running AD5933 (impedance analyzer) I2C example')
print('-'*40)

reg_map = {'creg1': 		0x80,  #MSBs
           'creg0': 		0x81,
           'start_f2': 		0x82,  # MSBs
           'start_f1': 		0x83,
           'start_f0': 		0x84,
           'incr_f2': 		0x85,  # MSBs
           'incr_f1': 		0x86,
           'incr_f0': 		0x87,
           'incr_num1': 	0x88,  # MSBs
           'incr_num0': 	0x89,
           'settle_cycle1': 0x8A,  # MSBs
           'settle_cycle0': 0x8B,
           'status': 		0x8F,
           'temp1': 		0x92,  # MSBs
           'temp0': 		0x93,
           'real_data1': 	0x94,  # MSBs
           'real_data0': 	0x95,
           'imag_data1': 	0x96,  # MSBs
           'imag_data0': 	0x97}

regs = []
for r in reg_map:
    regs.append(Register(name=r, address=reg_map[r],
                         read_write='R/W', is_config=True))

aardvark = AA()  # communication adapter
ad5933 = IC(regs, aardvark,
            interface='I2C', name='AD5933',
            slave_address=0x0D)

# check I2C reads
c1 = ad5933.get('creg1')
c0 = ad5933.get('creg0')

# Print the read-back.
print('Read from control reg: 0x{:02x}'.format(c1))
print('Read from control reg: 0x{:02x}'.format(c0))
