from migen import *
from migen.genlib.cdc import MultiReg
from shared.clkdiv import ClkDiv
from shared.pwm import PWM
from shared.board.fpga_dev_board import Platform
from shared.utils import delay
from shared.rotary_encoder import RotaryEncoder
from shared.seven_segment import SevenSegmentDisplay


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