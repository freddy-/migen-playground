from migen import *
from shared.board.fpga_dev_board import Platform
from shared.utils import delay
from shared.clkdiv import ClkDiv
from shared.pwm import PWM


class Main(Module):
    def __init__(self, platform):
        sysClkFreq = platform.clkFreq

        self.o_led = platform.request("green_led")

        self.submodules.pwm = pwm = PWM(sysClkFreq)
        self.submodules.timer = timer = ClkDiv(sysClkFreq, targetFreq=300)

        counter = Signal(8)
        direction = Signal()

        self.comb += [
            pwm.i_duty.eq(counter),
            pwm.i_enable.eq(1),
            self.o_led.eq(pwm.o_pwm),
            timer.i_enable.eq(1)
        ]

        self.sync += [
            If(timer.o_clk,
                If (direction,
                    counter.eq(counter - 1)
                ).Else(
                    counter.eq(counter + 1)
                ),

                If(counter == 254,
                    direction.eq(1)
                ).Elif(counter == 1,
                    direction.eq(0)
                )
            )
        ]


def generator(dut):
    yield dut.i_enable.eq(1)
    yield dut.i_duty.eq(50)
    yield from delay(512)


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "sim":
        dut = PWM(sysClkFreq=1)
        run_simulation(dut, generator(dut), vcd_name="test.vcd")

    else:
        platform = Platform()
        platform.build(Main(platform))
        platform.create_programmer().load_bitstream("build/top.bit")