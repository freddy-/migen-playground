#!/usr/bin/env python3

import time

from litex import RemoteClient

wb = RemoteClient()
wb.open()

# # #

# test buttons
print("Testing Buttons/Switches...")
while True:
    encoder = wb.regs.encoder_value.read()
    print("encoder: {}".format(encoder))
    wb.regs.display7Seg_value.write(encoder)
    time.sleep(0.1)

# # #

wb.close()
