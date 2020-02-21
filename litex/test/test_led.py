#!/usr/bin/env python3

import time
import random

from litex import RemoteClient

wb = RemoteClient(debug=True)
wb.open()

# # #

print(wb.regs.led_out)

# Test led
print("Testing Led...")
for i in range(64):
    wb.regs.led_out.write(i)
    time.sleep(0.5)

# # #

wb.close()
