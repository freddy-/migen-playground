from migen import *
from migen.genlib.cdc import MultiReg
from shared.clkdiv import ClkDiv
from shared.debouncer import Debouncer
from shared.pwm import PWM
from shared.board.fpga_dev_board import Platform
from shared.utils import delay

from shared.seven_segment import SevenSegmentDisplay

class RotaryEncoder(Module):
    def __init__(self, sysClkFreq):
        self.i_a = Signal()
        self.i_b = Signal()
        self.o_en = Signal()
        self.o_dir = Signal()
        self.o_counter = Signal(8)

        #  #  #

        a = Signal()
        b = Signal()
        syncA = Signal(4)
        syncB = Signal(4)

        self.submodules.debouncer_a = debouncer_a = Debouncer(sysClkFreq)
        self.submodules.debouncer_b = debouncer_b = Debouncer(sysClkFreq)

        self.comb += [
            debouncer_a.i_raw.eq(self.i_a),
            debouncer_b.i_raw.eq(self.i_b),
            a.eq(debouncer_a.o_clean),
            b.eq(debouncer_b.o_clean),

            self.o_en.eq(syncA[2] ^ syncA[3] ^ syncB[2] ^ syncB[3]),
            self.o_dir.eq(syncA[2] ^ syncB[3])
        ]

        self.sync += [
            syncA.eq(Cat(a, syncA)),
            syncB.eq(Cat(b, syncB)),

            If(self.o_en,
                If(self.o_dir,
                    self.o_counter.eq(self.o_counter + 1)
                ).Else(
                    self.o_counter.eq(self.o_counter - 1)
                )
            )
        ]

class Main(Module):
    def __init__(self, platform):
        sysClkFreq = platform.clkFreq

        encoderPins = platform.request("encoder")
        displayPins = platform.request("seven_seg")
        ledPin = platform.request("green_led")

        self.submodules.encoder = encoder = RotaryEncoder(sysClkFreq)
        self.submodules.display = display = SevenSegmentDisplay(sysClkFreq)
        self.submodules.pwm = pwm = PWM(sysClkFreq)

        self.comb += [
            encoder.i_a.eq(encoderPins.a),
            encoder.i_b.eq(encoderPins.b),

            pwm.i_enable.eq(1),
            pwm.i_duty.eq(encoder.o_counter),
            ledPin.eq(pwm.o_pwm),

            display.i_value.eq(encoder.o_counter),
            displayPins.digits.eq(~display.o_digits),
            displayPins.segments.eq(~display.o_segments)
        ]
        

def generator(dut):
    yield from delay(10)

    yield dut.i_a.eq(1)
    yield from delay(4)
    yield dut.i_b.eq(1)
    yield from delay(4)
    yield dut.i_a.eq(0)
    yield from delay(4)
    yield dut.i_b.eq(0)
    yield from delay(4)
    yield dut.i_a.eq(1)
    yield from delay(4)
    yield dut.i_b.eq(1)
    yield from delay(4)
    yield dut.i_a.eq(0)
    yield from delay(4)
    yield dut.i_b.eq(0)

    yield from delay(50)

    yield dut.i_b.eq(1)
    yield from delay(4)
    yield dut.i_a.eq(1)
    yield from delay(4)
    yield dut.i_b.eq(0)
    yield from delay(4)
    yield dut.i_a.eq(0)
    yield from delay(4)
    yield dut.i_b.eq(1)
    yield from delay(4)
    yield dut.i_a.eq(1)
    yield from delay(4)
    yield dut.i_b.eq(0)
    yield from delay(4)
    yield dut.i_a.eq(0)

    yield from delay(50)

if __name__ == "__main__":
    import sys

    if sys.argv[1] == "sim":
        dut = RotaryEncoder(sysClkFreq=1)
        run_simulation(dut, generator(dut), vcd_name="test.vcd")

    else:
        platform = Platform()
        main = Main(platform)
        platform.build(main)
        platform.create_programmer().load_bitstream("build/top.bit")