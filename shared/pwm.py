from migen import *
from .clkdiv import ClkDiv

class PWM(Module):
    def __init__(self, sysClkFreq):
        self.i_duty = Signal(8)
        self.i_enable = Signal()
        self.o_pwm = Signal()

        #  #  #

        counter = Signal(8)

        self.submodules.clkDiv = clkDiv = ClkDiv(sysClkFreq, targetFreq=2560000)

        self.sync += [
            If(self.i_enable,
                clkDiv.i_enable.eq(1),
                If(clkDiv.o_clk,
                    counter.eq(counter + 1)
                )                
            ).Else(
                clkDiv.i_enable.eq(0),
                counter.eq(0)
            )
        ]

        self.comb += [
            If(self.i_enable,
                If(counter < self.i_duty,
                    self.o_pwm.eq(1)
                ).Else(
                    self.o_pwm.eq(0)
                )
            ).Else(
                self.o_pwm.eq(0)
            )
        ]