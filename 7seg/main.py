from migen import *
from shared.board.fpga_dev_board import Platform
from shared.utils import delay
from shared.clkdiv import ClkDiv
from shared.seven_segment import SevenSegmentDisplay, BinaryToDecimalConverter, BcdTo7Segment

class Main(Module):
    def __init__(self, platform, clkFreq):
        display = platform.request("seven_seg")
        sevenSegDisplay = SevenSegmentDisplay(clkFreq)

        self.submodules += sevenSegDisplay

        self.comb += [
            sevenSegDisplay.i_value.eq(1234),
            display.digits.eq(~sevenSegDisplay.o_digits),
            display.segments.eq(~sevenSegDisplay.o_segments)
        ]


def bcdGenerator(dut):
    yield dut.i_value.eq(1234)
    yield from delay(100)

def sevenSegDecoderGenerator(dut):
    yield dut.i_bcd.eq(0)
    yield from delay(3)
    yield dut.i_bcd.eq(1)
    yield from delay(3)
    yield dut.i_bcd.eq(2)
    yield from delay(3)
    yield dut.i_bcd.eq(3)
    yield from delay(3)
    yield dut.i_bcd.eq(4)
    yield from delay(3)
    yield dut.i_bcd.eq(5)
    yield from delay(3)
    yield dut.i_bcd.eq(6)
    yield from delay(3)
    yield dut.i_bcd.eq(7)
    yield from delay(3)
    yield dut.i_bcd.eq(8)
    yield from delay(3)
    yield dut.i_bcd.eq(9)
    yield from delay(5)

def sevenSegGenerator(dut):
    yield dut.i_value.eq(1234)
    yield from delay(5000)
    
if __name__ == "__main__":
    import sys

    if sys.argv[1] == "sim-bcd":
        dut = BinaryToDecimalConverter()
        run_simulation(dut, bcdGenerator(dut), vcd_name="test.vcd")

    if sys.argv[1] == "sim-7seg-dec":
        dut = BcdTo7Segment()
        run_simulation(dut, sevenSegDecoderGenerator(dut), vcd_name="test.vcd")
    
    if sys.argv[1] == "sim-7seg":
        dut = SevenSegmentDisplay(100000)
        run_simulation(dut, sevenSegGenerator(dut), vcd_name="test.vcd")

    else:
        platform = Platform()
        clkFreq = platform.default_clk_period * 1000000
        main = Main(platform, clkFreq)
        platform.build(main)
        platform.create_programmer().load_bitstream("build/top.bit")