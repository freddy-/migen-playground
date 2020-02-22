#!/usr/bin/env python3

import time

from litex import RemoteClient

wb = RemoteClient()
wb.open()

# # #

def display_write(val):
  wb.regs.display7Seg_value.write(val)

for i in range(9999):
    display_write(i)
    time.sleep(0.05)

# # #

wb.close()
