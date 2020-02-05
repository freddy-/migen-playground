from migen import *
from shared.board.fpga_dev_board import Platform

class Blink(Module):
    def __init__(self, platform):
        self.green_led = green_led = platform.request("green_led")
        self.orange_led = orange_led = platform.request("orange_led")

        counter = Signal(25)
 
        self.sync += counter.eq(counter + 1)
        self.comb += [
            green_led.eq(counter[24]),
            orange_led.eq(~counter[24])
        ]

def generator(dut):
    for i in range(100):
        yield

if __name__ == "__main__":
    import sys

    if sys.argv[1] == "sim":
        dut = Blink(Platform())
        run_simulation(dut, generator(dut), vcd_name="test.vcd")
    else:
        platform = Platform()
        platform.build(Blink(platform))
        platform.create_programmer().load_bitstream("build/top.bit")