
lia.read_buffer.unstage()
lia.read_buffer.stage()
print('Starting scan')
lia.read_buffer.trigger()
time.sleep(0.2)
uid = RE(scan([lia.read_buffer, lia.isum],
                fg.freq, 4997, 5005, 12),
            LiveTable([fg.freq, lia.read_buffer, lia.isum]),
            # the input parameters below will be metadata
            attenuator='60dB',
            purpose='demo',
            operator='Lucas')