# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

from instrument_opening import *

usb, not_in_cfg = detect_instruments()
cfg = user_input(not_in_cfg[1])  # requires User input


append_to_yaml(cfg)
