from migen import *
from .clkdiv import ClkDiv

class Debouncer(Module):
    def __init__(self, sysClkFreq):
        self.i_raw = Signal()
        self.o_clean = Signal()

        debouncedOutput = Signal()
        counter = Signal(8)

        self.submodules.clkDiv = clkDiv = ClkDiv(sysClkFreq, targetFreq=800000)

        self.comb += [
          self.o_clean.eq(debouncedOutput),
          clkDiv.i_enable.eq(1)
        ]


        self.sync += [
            If(self.clkDiv.o_clk,
                counter.eq(Cat(~self.i_raw, counter[:-1]))
            ),

            If(counter == 0xFF,
                debouncedOutput.eq(1)
            ).Elif(counter == 0x00,
                debouncedOutput.eq(0)
            ).Else(
                debouncedOutput.eq(debouncedOutput)
            )
        ]