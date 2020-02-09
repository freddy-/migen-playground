from migen import *

class ClkDiv(Module):
    def __init__(self, sysClkFreq, targetFreq):
        self.o_clk = Signal()
        self.i_enable = Signal()
        
        #  #  #
        
        divideBy = int(sysClkFreq // targetFreq)
        counter = Signal(max=divideBy + 2)

        self.sync += [
            If(self.i_enable,
                If(counter == divideBy,
                    counter.eq(0),
                    self.o_clk.eq(1)
                ).Else(
                    counter.eq(counter + 1),
                    self.o_clk.eq(0)
                )
            ).Else(
                counter.eq(0),
                self.o_clk.eq(0)
            )
        ]
