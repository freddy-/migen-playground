from migen import *
from shared.board.fpga_dev_board import Platform
from shared.utils import delay
from shared.clkdiv import ClkDiv


class BinaryToDecimalConverter(Module):
    def __init__(self):
        self.i_value = Signal(16)
        self.o_thousands = Signal(4)
        self.o_hundreds = Signal(4)
        self.o_tens = Signal(4)
        self.o_ones = Signal(4)

        #  #  #

        value = Signal(16)
        register = Signal(32)
        thousands = Signal(4)
        hundreds = Signal(4)
        tens = Signal(4)
        ones = Signal(4)
        counter = Signal(max=20)

        self.submodules.bcd_fsm = FSM(reset_state="IDLE")
        self.bcd_fsm.act("IDLE",
            If(value != self.i_value,
                NextValue(register, self.i_value),
                NextValue(value, self.i_value),
                NextValue(counter, 0),
                NextState("SHIFT")
            )
        )
        self.bcd_fsm.act("SHIFT",
            NextValue(register, Cat(0, register)),
            If(counter >= 15,
                NextState("FINISH")
            ).Else(
                NextValue(counter, counter + 1),
                NextState("EXTRACT_NIBBLES")
            )
        )
        self.bcd_fsm.act("EXTRACT_NIBBLES",
            NextValue(thousands, register[28:32]),
            NextValue(hundreds, register[24:28]),
            NextValue(tens, register[20:24]),
            NextValue(ones, register[16:20]),
            NextState("ADD")
        )
        self.bcd_fsm.act("ADD",
            If(hundreds >= 5,
                NextValue(hundreds, hundreds + 3)
            ).Else(
                NextValue(hundreds, hundreds)
            ),
            If(tens >= 5,
                NextValue(tens, tens + 3)
            ).Else(
                NextValue(tens, tens)
            ),
            If(ones >= 5,
                NextValue(ones, ones + 3)
            ).Else(
                NextValue(ones, ones)
            ),
            NextState("CONCAT")
        )
        self.bcd_fsm.act("CONCAT",
            NextValue(register, Cat(register[:16], ones, tens, hundreds, thousands)),
            NextState("SHIFT")
        )
        self.bcd_fsm.act("FINISH",
            NextValue(self.o_thousands, register[28:32]),
            NextValue(self.o_hundreds, register[24:28]),
            NextValue(self.o_tens, register[20:24]),
            NextValue(self.o_ones, register[16:20]),
            NextState("IDLE")
        )

class BcdTo7Segment(Module):
    def __init__(self):
        self.i_bcd = Signal(4)
        self.o_7seg = Signal(8)

        #  #  #

        self.comb += Case(self.i_bcd, {
            0b0000: self.o_7seg.eq(0b00111111),
            0b0001: self.o_7seg.eq(0b00000110),
            0b0010: self.o_7seg.eq(0b01011011),
            0b0011: self.o_7seg.eq(0b01001111),
            0b0100: self.o_7seg.eq(0b01100110),
            0b0101: self.o_7seg.eq(0b01101101),
            0b0110: self.o_7seg.eq(0b01111101),
            0b0111: self.o_7seg.eq(0b00000111),
            0b1000: self.o_7seg.eq(0b01111111),
            0b1001: self.o_7seg.eq(0b01101111),
            "default": self.o_7seg.eq(0)
        })


class SevenSegmentDisplay(Module):
    def __init__(self, sysFreq):
        self.i_value = Signal(16)
        self.o_digits = Signal(4)
        self.o_segments = Signal(8)

        #  #  #

        digitCounter = Signal(4, reset=0b1000)
        clockDiv = ClkDiv(sysFreq, 196)  # 196Hz ~5ms
        bcdConverter = BinaryToDecimalConverter()
        thousandsConverter = BcdTo7Segment()
        hundredesConverter = BcdTo7Segment()
        tensConverter = BcdTo7Segment()
        onesConverter = BcdTo7Segment()

        self.submodules += clockDiv, bcdConverter, thousandsConverter, hundredesConverter, tensConverter, onesConverter

        self.comb += [
            clockDiv.i_enable.eq(1),

            thousandsConverter.i_bcd.eq(bcdConverter.o_thousands),
            hundredesConverter.i_bcd.eq(bcdConverter.o_hundreds),
            tensConverter.i_bcd.eq(bcdConverter.o_tens),
            onesConverter.i_bcd.eq(bcdConverter.o_ones),

            bcdConverter.i_value.eq(self.i_value),

            self.o_digits.eq(digitCounter)
        ]

        self.sync += [
            If(clockDiv.o_clk,
                digitCounter.eq(Cat(digitCounter[1:], digitCounter[0]))
            ),
            
            Case(digitCounter, {
                0b1000: self.o_segments.eq(thousandsConverter.o_7seg),
                0b0100: self.o_segments.eq(hundredesConverter.o_7seg),
                0b0010: self.o_segments.eq(tensConverter.o_7seg),
                "default": self.o_segments.eq(onesConverter.o_7seg)
            })
        ]


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