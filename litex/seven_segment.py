from migen import *
from shared.seven_segment import SevenSegmentDisplay as _SevenSegmentDisplay
from litex.soc.interconnect.csr import AutoCSR, CSRStorage
from litex.soc.integration.doc import ModuleDoc

class SevenSegmentDisplay(Module, AutoCSR, ModuleDoc):
    """SevenSegmentDisplay
        dsdfssdfsdf
    """
    def __init__(self, sys_clk_freq, displayPins):
        self.value = CSRStorage(16, description="Value to show in 7 segment display.")

        self.submodules.display = _SevenSegmentDisplay(sys_clk_freq)

        self.comb += [
            displayPins.digits.eq(~self.display.o_digits),
            displayPins.segments.eq(~self.display.o_segments)
        ]

        self.sync += [
            If(self.value.re,
                self.display.i_value.eq(self.value.storage)
            )
        ]